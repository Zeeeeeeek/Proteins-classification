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


def to_csv_kmer_count(df_path, k: int, output_path):
    df = pd.read_csv(df_path, usecols=["region_id", "class_topology_fold_clan", "sequence"])
    writer = KmerCsvWriter(output_path, non_kmer_columns=["region_id", "class_topology_fold_clan", "sequence"], k=k)
    for index, row in df.iterrows():
        if row['sequence'] is None or row['sequence'] == "":
            continue
        writer.write_kmer_count(kmer_count(k, row['sequence']), [row['region_id'], row['class_topology_fold_clan'],
                                                                 row['sequence']])
    writer.close()
