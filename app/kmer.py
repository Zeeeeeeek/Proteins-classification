import os
import threading

import numpy as np
import pandas as pd

from data_preprocessing import split_df_into_n
import logging

logging.basicConfig(filename='kmer.log', level=logging.INFO, format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')


def kmer_count(k, sequence):
    """
    Count the number of k-mers in a sequence.
    :param k: int
    :param sequence: str
    :return: dict
    """
    kmer_dict = {}
    if type(sequence) != str:
        return kmer_dict
    for i in range(len(sequence) - k + 1):
        kmer = sequence[i:i + k]
        if kmer in kmer_dict:
            kmer_dict[kmer] += 1
        else:
            kmer_dict[kmer] = 1
    return kmer_dict


def kmer_count_dataframe(k, df):
    """
    Count the number of k-mers in a dataframe.
    :param k: int
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    copy_df = df[["region_id", "class_topology_fold_clan", "sequence"]].copy()
    kmer_set = set()
    for index, row in df.iterrows():
        if row['sequence'] is None or row['sequence'] == "":
            continue
        kmer_dict = kmer_count(k, row['sequence'])
        for kmer, count in kmer_dict.items():
            kmer_set.add(kmer)
            copy_df.at[index, kmer] = count
    for kmer_col in kmer_set:
        copy_df[kmer_col] = copy_df[kmer_col].fillna(0).astype(np.uint16)
    return copy_df


def multithread_kmer_count_df(df_path, k, output_path, n_threads=5):
    df = pd.read_csv(df_path)
    dfs = split_df_into_n(df, 5 if n_threads < 5 else n_threads)
    count = 0
    for index, sub_df in enumerate(dfs):
        ext(sub_df, index, k, n_threads)
        count = index + 1
    logging.info(f"Merging {count} files")
    merge_csv_files(output_path, count, 100)


def ext(df, df_index, k, n_threads=5):
    def worker_function(sdf, worker_k, result_list):
        result_list.append(kmer_count_dataframe(worker_k, sdf))

    chunks = split_df_into_n(df, 5 if n_threads < 5 else n_threads)
    chunk_threads = []
    merged_dfs = []
    logging.info(f"Subdf shape: {df.shape}")
    for chunk in chunks:
        logging.info(f"Chunk shape: {chunk.shape}")
        t = threading.Thread(target=worker_function, args=(chunk, k, merged_dfs))
        chunk_threads.append(t)
        t.start()
    for t in chunk_threads:
        t.join()
    merged_df = pd.concat(merged_dfs, ignore_index=True)
    merged_df.to_csv(f"cache_{df_index}.csv", index=False)
    logging.info(f"Cached subdf {df_index}")

def merge_csv_files(output_path, count, CHUNK_SIZE):
    for i in range(count):
        chunk_container = pd.read_csv(f"cache_{i}.csv", chunksize=CHUNK_SIZE)
        for chunk in chunk_container:
            if i == 0:
                chunk.to_csv(f"{output_path}.csv", mode='w', index=False)
            else:
                chunk.to_csv(f"{output_path}.csv", mode='a', header=False, index=False)

    for i in range(count):
        os.remove(f"cache_{i}.csv")
