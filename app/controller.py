import re

from app.api import repeatsdb_get
from app.data_preprocessing import preprocess_from_json
from app.kmer import multithread_kmer_count_df

COLON_PATTERN = re.compile(r'^(?:[^:]+:)+[^:]+$')


def check_query_string(query_string):
    if not COLON_PATTERN.match(query_string):
        raise ValueError("Query string must be in the form of \"field:value\".")


def run_query(query_string, file_name, merge_regions):
    q = "".join(query_string)
    check_query_string(q)
    q = q.replace("+", "%2B").replace("|", "%7C")
    q += "%2Breviewed:true&show=entries"
    preprocess_from_json(repeatsdb_get("query=" + q), merge_regions).to_csv("csv/" + file_name + ".csv", index=False)


def run_kmer_count(input_file, k, output_file):
    input_name = input_file if input_file.endswith(".csv") else input_file + ".csv"
    output_name = output_file + ".csv" if output_file is not None else input_file + "_" + str(k) + "_mer.csv"
    multithread_kmer_count_df("csv/" + input_name, k).to_csv("kmers/" + output_name, index=False)