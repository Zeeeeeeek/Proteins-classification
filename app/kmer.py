import os
import threading
import numpy as np
import pandas as pd
from memory_profiler import profile

from app.KmerCsvWriter import KmerCsvWriter
from pympler import asizeof
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s', filemode='w', filename='memory.log')

def kmer_count(k, sequence):
    """
    Count the number of k-mers in a sequence.
    :param k: Int
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
    :param k: Int
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
        copy_df[kmer_col] = copy_df[kmer_col].astype(pd.SparseDtype(np.uint16, np.nan))
    return copy_df


def multithread_kmer_count_df(df_path: object, k: int, output_path: object, n_threads: int = 5) -> object:
    if os.path.exists(output_path):
        raise FileExistsError(f"Error: {output_path} already exists.")
    if k < 1:
        raise ValueError("Error: k must be greater than 0.")
    if n_threads < 1:
        raise ValueError("Error: n_threads must be greater than 0.")
    if n_threads == 1:
        kmer_count_dataframe(k, pd.read_csv(df_path)).to_csv(output_path, index=False)
        return
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan", "sequence"])

    def worker_function(sdf, worker_k, result_list):
        result_list.append(kmer_count_dataframe(worker_k, sdf))

    splits = [df[i::n_threads] for i in range(n_threads)]
    threads = []
    dfs = []
    for split in splits:
        t = threading.Thread(target=worker_function, args=(split, k, dfs))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    pd.concat(dfs, ignore_index=True).to_csv(output_path, index=False)

def new_kmer_count(df_path, k: int, output_path):
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan", "sequence"])
    writer = KmerCsvWriter(output_path)
    for index, row in df.iterrows():
        if row['sequence'] is None or row['sequence'] == "":
            continue
        to_profile(writer, k, row['sequence'], row['region_id'], row['class_topology_fold_clan'])
        logging.debug(f"Memory usage: {asizeof.asizeof(writer) / (1024 * 1024)} MB")
    writer.close()

@profile
def to_profile(writer, k, sequence, region_id, class_topology_fold_clan):
    writer.write_kmer_count(kmer_count(k, sequence), region_id, class_topology_fold_clan, sequence)
