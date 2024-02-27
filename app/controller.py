import re

from app.api import repeatsdb_get
from app.data_preprocessing import preprocess_from_json
from app.kmer import single_thread_kmer_count
from app.models import run_models

COLON_PATTERN = re.compile(r'^(?:[^:]+:)+[^:]+$')


def check_query_string(query_string):
    if not COLON_PATTERN.match(query_string):
        raise ValueError("Query string must be in the form of \"field:value\".")


def run_query(query_string, file_name, merge_regions, n_threads):
    q = "".join(query_string)
    check_query_string(q)
    q = q.replace("+", "%2B").replace("|", "%7C")
    q += "%2Breviewed:true&show=entries"
    output = file_name if file_name else "output.csv"
    if not output.endswith(".csv"):
        output += ".csv"
    preprocess_from_json(repeatsdb_get("query=" + q), merge_regions, n_threads) \
        .to_csv(file_name, index=False)


def run_kmer_count(input_file, k, output_file):
    input_name = input_file if input_file.endswith(".csv") else input_file + ".csv"
    output_name = output_file if output_file is not None else input_file + "_" + str(k) + "_mer.csv"
    if not output_name.endswith(".csv"):
        output_name += ".csv"
    single_thread_kmer_count(input_name, k, output_name)

def run_models_on_kmers(path, level, method, max_sample_size_per_level):
    run_models(
        path if path.endswith(".csv") else path + ".csv",
        level,
        method,
        max_sample_size_per_level
    )
