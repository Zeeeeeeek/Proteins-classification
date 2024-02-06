from datetime import datetime

import pandas as pd
from api import pdb_get
from Bio.PDB import PDBParser
from io import StringIO
import threading
import warnings
import logging
import re
import collections

logging.basicConfig(filename=f"log/{datetime.now().strftime('%d_%H_%M_%S')}_preprocessing.log",
                    format="%(levelname)s %(asctime)s,%(msecs)d %(message)s",
                    datefmt="%H:%M:%S",
                    filemode="w")

warnings.filterwarnings("ignore")

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
        case _:
            return "X"


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
                    # elif prev_model is not None and prev_model == model:
                    else:
                        # An atom's id with number and letter combination may have been used
                        alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
                        for letter in alphabet:
                            if str(residue.get_full_id()[3][1]) + letter not in res_dict.keys():
                                res_dict[str(residue.get_full_id()[3][1]) + letter] = residue.get_resname()
                                break
                if residue.get_full_id()[3][1] > end:
                    return res_dict
        if len(res_dict) > 0:  # A model has been found and used, finding other models with the same chain may lead to errors
            return res_dict
    return res_dict


def extract_remark_465(pdb_string, chain_id, start, end):
    remark_465 = []
    met_remark_465 = False
    for line in pdb_string.split("\n"):
        if line.startswith("REMARK 465"):
            met_remark_465 = True
            remark_465.append(line.split()[2:])
        elif met_remark_465:
            break
    if len(remark_465) < 7:
        return {}
    remark_465 = remark_465[7:]
    res_dict = {}
    for line in remark_465:
        try:
            index = int(line[2])
        except ValueError:  # A combination of atom id and letters may have been used
            index = int(re.search(r'\d+', line[2]).group())
        if line[1] == chain_id and start <= index <= end:
            res_dict[str(line[2])] = line[0]
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


def lambda_sequence(row):
    pdb_id = row["pdb_id"]
    row_chain = row["pdb_chain"]
    pdb_parser = PDBParser(QUIET=True)
    pdb = pdb_get(pdb_id)
    if pdb is None or pdb == "":
        logging.error(f"Empty pdb for {pdb_id}\n")
        return None
    pdb_io = StringIO(pdb)
    structure = pdb_parser.get_structure(pdb_id, pdb_io)
    start = int(row["start"])
    end = int(row["end"])
    res_dict = extract_res_dict(structure, row_chain, start, end)
    if len(res_dict) != (end - start + 1):
        remarks = extract_remark_465(pdb, row_chain, start, end)
        res_dict.update(remarks)
    sequence = ""
    try:
        sorted_res_dict = collections.OrderedDict(sorted(res_dict.items(), key=lambda item: custom_key(item[0])))
    except TypeError:
        print(res_dict.items())  # Todo remove
        print(pdb_id, row_chain, start, end)
        raise
    for value in sorted_res_dict.values():
        sequence += three_residue_to_one(value)
    if len(sequence) != (end - start + 1):
        logging.error(
            f"Sequence length mismatch for pdb_id: {pdb_id} pdb_chain: {row_chain} start: {start} end: {end}\n"
            f"Expected length: {end - start + 1}, actual length: {len(sequence)}\n"
            f"Sequence: {sequence}\n"
        )
    return sequence


def remove_rows_with_errors(df):
    """
    Rimuove le righe con errori dimostrati nel notebook, funzione temporanea in vista di correzioni
    """
    output_df = df.copy()
    # Rimuove le righe con start > end
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


def preprocess_from_json(json, regions, outputname, format):
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
    dfs = split_df_into_n(df, 20)
    for d in dfs:
        t = threading.Thread(target=thread_worker, args=(d,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    df = pd.concat(dfs)
    if format == "csv":
        df.to_csv("csv/" + outputname + ".csv", index=False)
