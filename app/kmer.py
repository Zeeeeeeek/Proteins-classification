import shutil
import threading

import numpy as np
import pandas as pd
import os

from data_preprocessing import split_df_into_n
import logging

logging.basicConfig(filename='kmer.log', level=logging.INFO, format='%(asctime)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S', filemode='w')

def memory_usage_df(df):
    mem = round(df.memory_usage().sum() * 0.000001, 3)
    return str(mem)

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
            copy_df.at[index, kmer] = count if count > 0 else np.nan
    kmer_col_type = np.uint16 if k > 6 else np.uint8
    for kmer_col in kmer_set:
        copy_df[kmer_col] = copy_df[kmer_col].astype(pd.SparseDtype(kmer_col_type, np.nan))
    return copy_df


def merge_temp_files(length, output_path, cache_path):
    for i in range(length):
        df = pd.read_hdf(f"{cache_path}/temp_{i}.h5", index=False, key="df")
        if i == 0:
            df.to_csv(output_path, index=False)
        else:
            left = pd.read_csv(output_path)
            merged = pd.concat([left, df], ignore_index=True)
            merged.to_csv(output_path, index=False)
            del left, merged
        del df
    shutil.rmtree(cache_path)


def multithread_kmer_count_df(df_path, k: int, output_path, n_threads: int = 5):
    if k <= 0:
        raise ValueError("k must be a positive integer")
    base = 100
    if k <= 5:
        size = 1000
    elif 5 < k < 9:
        size = base + 2 ** (10 - k)
    else:
        size = base
    chunk_container = pd.read_csv(df_path, chunksize=size)
    cache_path = os.path.join(os.path.dirname(output_path), "/cache")
    #if not os.path.exists(cache_path):
    #    os.makedirs(cache_path)
    #else:
    #    for file in os.listdir(cache_path):
    #        os.remove(os.path.join(cache_path, file))
    length = 0
    output_df = pd.DataFrame()
    for index, chunk in enumerate(chunk_container):
        kdf = kmer_count_chunk(chunk, k, index, cache_path, n_threads)
        output_df = pd.concat([output_df, kdf], ignore_index=True)
        logging.info(f"Output_df memory usage: {memory_usage_df(output_df)} MB")
        logging.info(f"Kdf memory usage: {memory_usage_df(kdf)} MB")
        length = index + 1
    output_df.to_csv(output_path, index=False)
    #merge_temp_files(length, output_path, cache_path)


def kmer_count_chunk(df, k, index, cache_path, n_threads=5):
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
    return pd.concat(merged_dfs, ignore_index=True)
    #merged.to_hdf(f"{cache_path}/temp_{index}.h5", index=False, key="df", mode="w")
    #logging.info(f"Saved chunk {index}")
