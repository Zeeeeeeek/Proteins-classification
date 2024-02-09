import threading

import numpy as np
import pandas as pd

from app.data_preprocessing import split_df_into_n


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
    copy_df = df[["repeatsdb_id", "sequence"]].copy()
    kmer_set = set()
    for index, row in df.iterrows():
        if row['sequence'] is None or row['sequence'] == "":
            continue
        kmer_dict = kmer_count(k, row['sequence'])
        for kmer, count in kmer_dict.items():
            kmer_set.add(kmer)
            copy_df.at[index, kmer] = count
    for kmer_col in kmer_set:
        copy_df[kmer_col] = copy_df[kmer_col].replace(np.nan, 0)
    return copy_df


def multithread_kmer_count_df(df_path, k, n_threads=10):
    df = pd.read_csv(df_path)
    threads = []
    dfs = split_df_into_n(df, n_threads)
    merged_dfs = []

    def worker_function(sdf, worker_k, result_list):
        result_list.append(kmer_count_dataframe(worker_k, sdf))

    for sub_df in dfs:
        t = threading.Thread(target=worker_function, args=(sub_df, k, merged_dfs))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()
    return pd.concat(merged_dfs, ignore_index=True).replace(np.nan, 0)
