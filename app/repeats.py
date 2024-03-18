import pandas as pd
from app.api import repeatsdb_get
import threading
import warnings

from app.protein_sequences import get_sequence

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


def add_sequence_to_row(row):
    return get_sequence(row["pdb_id"], row["pdb_chain"], int(row["start"]), int(row["end"]))


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


def query_repeatsdb_to_csv(query_classes, merge_regions, n_threads, output_file):
    if not all(c in ['2', '3', '4', '5'] for c in query_classes):
        raise ValueError("Query classes must be in  ['2', '3', '4', '5'].")
    query = "class:" + "%7Cclass:".join(set(query_classes))
    query += "%2Breviewed:true&show=entries"
    df = preprocess_from_json(repeatsdb_get("query=" + query), merge_regions, n_threads)
    df = df[df["class"].isin(query_classes)]
    df.to_csv(output_file, index=False)


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

    def thread_worker(worker_df):
        worker_df.loc[:, "sequence"] = worker_df.apply(add_sequence_to_row, axis=1)

    warnings.filterwarnings("ignore")  # Suppress warnings from BioPython
    for d in dfs:
        t = threading.Thread(target=thread_worker, args=(d,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    warnings.filterwarnings("default")
    return pd.concat(dfs)
