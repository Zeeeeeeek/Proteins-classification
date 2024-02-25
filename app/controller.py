import re

from api import repeatsdb_get
from data_preprocessing import preprocess_from_json
from kmer import single_thread_kmer_count, kmer_count_multithread

COLON_PATTERN = re.compile(r'^(?:[^:]+:)+[^:]+$')


def check_query_string(query_string):
    if not COLON_PATTERN.match(query_string):
        raise ValueError("Query string must be in the form of \"field:value\".")


def run_query(query_string, file_name, merge_regions, n_threads):
    q = "".join(query_string)
    check_query_string(q)
    q = q.replace("+", "%2B").replace("|", "%7C")
    q += "%2Breviewed:true&show=entries"
    preprocess_from_json(repeatsdb_get("query=" + q), merge_regions, n_threads) \
        .to_csv(file_name + ".csv", index=False)


def run_kmer_count(input_file, k, output_file, n_threads=5):
    input_name = input_file if input_file.endswith(".csv") else input_file + ".csv"
    output_name = output_file if output_file is not None else input_file + "_" + str(k) + "_mer.csv"
    if not output_name.endswith(".csv"):
        output_name += ".csv"
    if n_threads == 1:
        single_thread_kmer_count(input_name, k, output_name)
    else:
        kmer_count_multithread(input_name, k, output_name, n_threads)
