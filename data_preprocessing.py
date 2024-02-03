import pandas as pd
from api import pdb_get
from Bio.PDB import PDBParser
from io import StringIO

columns_to_ignore = (["reviewed", "annotator", "origin"])

aminoacids = {
    "ALA": "A",
    "CYS": "C",
    "ASP": "D",
    "GLU": "E",
    "PHE": "F",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LYS": "K",
    "LEU": "L",
    "MET": "M",
    "ASN": "N",
    "PYL": "O",
    "PRO": "P",
    "GLN": "Q",
    "ARG": "R",
    "SER": "S",
    "THR": "T",
    "SEC": "U",
    "VAL": "V",
    "TRP": "W",
    "TYR": "Y",
    "MSE": "X", # Selenometionina (non standard) added with X as in repeatsdb
    "HYP": "X" # Idrossiprolina (non standard) added with X as in repeatsdb
}


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


def add_sequences(df):
    output_df = df.copy()
    for index, row in df.iterrows():
        pdb_id = row["pdb_id"]
        row_chain = row["pdb_chain"]
        pdb_parser = PDBParser(QUIET=True)
        pdb = StringIO(pdb_get(pdb_id))
        sequence = ""
        structure = pdb_parser.get_structure(pdb_id, pdb)
        start = int(row["start"])
        end = int(row["end"])
        for model in structure:
            for chain in model:
                if chain.id != row_chain:
                    continue
                for residue in chain:
                    if residue.get_full_id()[3][1] >= start:
                        try:
                            sequence += aminoacids[residue.get_resname()]
                        except KeyError:
                            with open("error_log.txt", "a") as f:
                                f.write(f"Error in {pdb_id} with residue {residue.get_resname()} at position {residue.get_full_id()[3][1]}\n\n")
                                f.write(f"Row:\n {row}\n\n")
                                f.write(f"Sequence: {sequence} + {residue.get_resname()}\n\n")
                            break
                    if residue.get_full_id()[3][1] == end:
                        break
        output_df.at[index, "sequence"] = sequence
    return output_df


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
    df = add_sequences(df)
    if format == "csv":
        df.to_csv(outputname + ".csv", index=False)
