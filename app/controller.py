import re
from typing import List

from app.repeats import query_repeatsdb_to_csv
from app.kmer import single_thread_kmer_count
from app.models import run_models

COLON_PATTERN = re.compile(r'^(?:[^:]+:)+[^:]+$')


def check_query_string(query_string):
    if not COLON_PATTERN.match(query_string):
        raise ValueError("Query string must be in the form of \"field:value\".")


def run_repeatsdb_query(query_classes: List[str], file_name, merge_regions, n_threads):
    output = file_name if file_name else "output.csv"
    if not output.endswith(".csv"):
        output += ".csv"
    query_repeatsdb_to_csv(query_classes, merge_regions, n_threads, output)


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
