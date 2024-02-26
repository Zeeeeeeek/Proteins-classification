import concurrent.futures
import queue
import pandas as pd

from app.KmerCsvWriter import KmerCsvWriter


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
    for i in range(1, k + 1):
        for j in range(len(sequence) - i + 1):
            kmer = sequence[j:j + i]
            if kmer in kmer_dict:
                kmer_dict[kmer] += 1
            else:
                kmer_dict[kmer] = 1
    return kmer_dict


def single_thread_kmer_count(df_path, k: int, output_path):
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan", "sequence"])
    writer = KmerCsvWriter(output_path)
    for index, row in df.iterrows():
        if row['sequence'] is None or row['sequence'] == "":
            continue
        writer.write_kmer_count(kmer_count(k, row['sequence']), row['region_id'], row['class_topology_fold_clan'],
                                row['sequence'])
    writer.close()


def kmer_count_multithread(df_path, k, output_path, n_threads):
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan", "sequence"])
    writer = KmerCsvWriter(output_path)
    q = queue.Queue()

    def worker_function(worker_row, worker_k):
        q.put(
            (
                kmer_count(worker_k, worker_row['sequence']), worker_row['region_id'],
                worker_row['class_topology_fold_clan'],
                worker_row['sequence']
            )
        )

    with concurrent.futures.ThreadPoolExecutor(max_workers=n_threads) as executor:
        for _, row in df.iterrows():
            executor.submit(worker_function, row, k)
        q.put(None)
    while True:
        t = q.get()
        if t is None:
            break
        writer.write_kmer_count(t[0], t[1], t[2], t[3])
    writer.close()
