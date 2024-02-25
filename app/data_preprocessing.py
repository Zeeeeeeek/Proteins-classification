import pandas as pd
from app.api import pdb_get, mmCIF_get
from Bio.PDB import PDBParser, MMCIFParser
from io import StringIO
import threading
import warnings
import collections

columns_to_ignore = (["reviewed", "annotator", "origin"])


def differentiate_units_ids(df):
    output_df = df.copy()
    counter = -1
    previous_id = df.iloc[0]["repeatsdb_id"]
    for index, row in df.iterrows():
        if previous_id == row["repeatsdb_id"]:
            counter += 1
        else:
            counter = 0
            previous_id = row["repeatsdb_id"]
        output_df.at[index, "repeatsdb_id"] = row["repeatsdb_id"] + "_" + str(counter)
    return output_df


def integrate_regions(df):
    grouped = df.groupby(["region_id"])
    output_df = pd.DataFrame()
    difference_columns = df.columns.difference(["region_id", "start", "end", "type"])
    for region_id, group in grouped:
        r = region_id[0].split("_")
        row = {
            "region_id": region_id[0],
            "start": r[1],
            "end": r[2],
            "type": group["type"].tolist()
        }
        for col in difference_columns:
            row[col] = group[col].iloc[0]
        output_df = pd.concat([output_df, pd.DataFrame([row])], ignore_index=True)
    return output_df


def three_residue_to_one(residue):
    match residue:
        case "ALA":
            return "A"
        case "CYS":
            return "C"
        case "ASP":
            return "D"
        case "GLU":
            return "E"
        case "PHE":
            return "F"
        case "GLY":
            return "G"
        case "HIS":
            return "H"
        case "ILE":
            return "I"
        case "LYS":
            return "K"
        case "LEU":
            return "L"
        case "MET":
            return "M"
        case "ASN":
            return "N"
        case "PYL":
            return "O"
        case "PRO":
            return "P"
        case "GLN":
            return "Q"
        case "ARG":
            return "R"
        case "SER":
            return "S"
        case "THR":
            return "T"
        case "SEC":
            return "U"
        case "VAL":
            return "V"
        case "TRP":
            return "W"
        case "TYR":
            return "Y"
        case "HOH":
            return ""
        case _:
            return "X"


def get_sequence_from_mmcif(file_mmcif, id_chain, start, end):
    parser = MMCIFParser(QUIET=True)
    structure = parser.get_structure('structure', file_mmcif)
    residues = extract_res_dict(structure, id_chain, start, end)
    sequence = ""
    sorted_res_dict = collections.OrderedDict(sorted(residues.items(), key=lambda item: custom_key(item[0])))
    for value in sorted_res_dict.values():
        sequence += three_residue_to_one(value)
    return sequence


def extract_res_dict(structure, chain_id, start, end):
    res_dict = {}
    for model in structure:
        for chain in model:
            if chain.id != chain_id:
                continue
            for residue in chain:
                if start <= residue.get_full_id()[3][1] <= end:
                    if str(residue.get_full_id()[3][1]) not in res_dict.keys():
                        res_dict[str(residue.get_full_id()[3][1])] = residue.get_resname()
                    else:
                        res_dict[str(residue.get_full_id()[3][1]) + residue.get_full_id()[3][2]] = residue.get_resname()
        if len(res_dict) > 0:  # A model has been found and used, finding other models with the same chain may lead to errors
            return res_dict
    return res_dict


def custom_key(key):
    parts = []
    current_part = ""
    is_negative = False

    for char in key:
        if char.isdigit() or (char == '-' and not current_part):
            # Check for the negative sign at the beginning of the part
            if char == '-' and not current_part:
                is_negative = True
            else:
                current_part += char
        else:
            if current_part:
                parts.append(int(current_part) * (-1 if is_negative else 1))
                current_part = ""
                is_negative = False
            parts.append(char)

    if current_part:
        parts.append(int(current_part) * (-1 if is_negative else 1))

    return parts


def get_missing_residues(structure, chain_id, start, end):
    missing_residues = {}
    for res in structure.header["missing_residues"]:
        if res['chain'] == chain_id and start <= res['ssseq'] <= end:
            if res['insertion'] is not None:
                id = str(res['ssseq']) + res['insertion']
            else:
                id = str(res['ssseq'])
            missing_residues[id] = res['res_name']
    return missing_residues


def lambda_sequence(row):
    pdb_id = row["pdb_id"]
    row_chain = row["pdb_chain"]
    pdb_parser = PDBParser(QUIET=True)
    pdb = pdb_get(pdb_id)
    if pdb is None:
        return get_sequence_from_mmcif(StringIO(mmCIF_get(pdb_id)), row_chain, int(row["start"]), int(row["end"]))
    pdb_io = StringIO(pdb)
    structure = pdb_parser.get_structure(pdb_id, pdb_io)
    start = int(row["start"])
    end = int(row["end"])
    res_dict = extract_res_dict(structure, row_chain, start, end)
    if len(res_dict) != (end - start + 1):
        remarks = get_missing_residues(structure, row_chain, start, end)
        res_dict.update(remarks)
    sequence = ""
    sorted_res_dict = collections.OrderedDict(sorted(res_dict.items(), key=lambda item: custom_key(item[0])))
    for value in sorted_res_dict.values():
        sequence += three_residue_to_one(value)
    return sequence


def remove_rows_with_errors(df):
    """
    Remove rows with start > end, and rows with region_id not matching min of starts and max of ends.
    """
    output_df = df.copy()
    # Remove rows with start > end
    output_df = output_df[~output_df['region_id'].isin(df[df['start'] > df['end']]['region_id'].tolist())]
    to_remove = set()
    agg = output_df.groupby('region_id').agg({
        'start': 'min',
        'end': 'max',
        'region_id': 'first'
    })
    for _, row in agg.iterrows():
        split = row['region_id'].split('_')
        if int(split[1]) != row['start'] or int(split[2]) != row['end']:
            to_remove.add(row['region_id'])
    return output_df[~output_df['region_id'].isin(to_remove)]


def split_df_into_n(df, n):
    """
    Split a dataframe into n dataframes.
    """
    return [df[i::n] for i in range(n)]


def thread_worker(df):
    df.loc[:, "sequence"] = df.apply(lambda_sequence, axis=1)


def preprocess_from_json(json, regions, n_threads=5):
    df = pd.DataFrame(json).drop(columns_to_ignore, axis=1)
    df = df.astype({
        "start": int,
        "end": int,
        "region_units_num": int,
        "region_average_unit_length": float
    })
    df = df.astype({
        col: str for col in df.columns.difference(["start", "end", "region_units_num", "region_average_unit_length"])
    })
    df = remove_rows_with_errors(df)
    df = integrate_regions(df) if regions else differentiate_units_ids(df)
    threads = []
    dfs = split_df_into_n(df, n_threads)
    warnings.filterwarnings("ignore")
    for d in dfs:
        t = threading.Thread(target=thread_worker, args=(d,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    warnings.filterwarnings("default")
    return pd.concat(dfs)
