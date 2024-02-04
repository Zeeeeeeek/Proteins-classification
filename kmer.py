def kmer_count(k, sequence):
    """
    Count the number of k-mers in a sequence.
    :param k: int
    :param sequence: str
    :return: dict
    """
    kmer_dict = {}
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
    copy_df = df.copy()
    kmer_set = set()
    for index, row in df.iterrows():
        if row['sequence'] is None or row['sequence'] == "":
            continue
        kmer_dict = kmer_count(k, row['sequence'])
        for kmer, count in kmer_dict.items():
            kmer_set.add(kmer)
            copy_df.at[index, kmer] = count
    for kmer_col in kmer_set:
        copy_df[kmer_col] = copy_df[kmer_col].fillna(0).astype(int)
    return copy_df
