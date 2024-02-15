import threading

import numpy as np
import pandas as pd

from data_preprocessing import split_df_into_n
import logging

logging.basicConfig(filename='kmer.log', level=logging.INFO, format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', filemode='w')


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


def multithread_kmer_count_df(df_path, k: int, output_path, n_threads: int = 5):
    if k <= 0:
        raise ValueError("k must be a positive integer")
    base = 100
    if k < 5:
        size = base + 2 ** (12 - k)
    elif 5 <= k < 9:
        size = base + 2 ** (10 - k)
    else:
        size = base + 2 ** (14 - k) if (14 - k) > 0 else base
    chunk_container = pd.read_csv(df_path, chunksize=size)
    for chunk in chunk_container:
        kmer_count_chunk(chunk, output_path, k, n_threads)


def kmer_count_chunk(df, output_path, k, n_threads=5):
    def worker_function(sdf, worker_k, result_list):
        result_list.append(kmer_count_dataframe(worker_k, sdf))

    splits = split_df_into_n(df, n_threads)
    chunk_threads = []
    merged_dfs = []
    logging.info(f"Subdf shape: {df.shape}")
    for split in splits:
        logging.info(f"Chunk shape: {split.shape}")
        t = threading.Thread(target=worker_function, args=(split, k, merged_dfs))
        chunk_threads.append(t)
        t.start()
    for t in chunk_threads:
        t.join()
    merged_df = pd.concat(merged_dfs, ignore_index=True)
    merged_df.to_json(output_path, index=False, mode="a")
