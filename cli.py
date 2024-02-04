import argparse

import pandas as pd

from api import repeatsdb_get
import re
from data_preprocessing import preprocess_from_json
import time

from kmer import kmer_count_dataframe

COLON_PATTERN = re.compile(r'^(?:[^:]+:)+[^:]+$')


def check_query_string(query_string):
    if not COLON_PATTERN.match(query_string):
        raise ValueError("Query string must be in the form of \"field:value\".")


def handle_query(args):
    q = "".join(args.query_string)
    check_query_string(q)
    q = q.replace("+", "%2B").replace("|", "%7C")
    q += "%2Breviewed:true&show=entries"
    preprocess_from_json(repeatsdb_get("query=" + q), args.merge_regions, args.file_name, args.output_format)


def handle_kmer(args):
    input_name = args.input if args.input.endswith(".csv") else args.input + ".csv"
    df = pd.read_csv(input_name)
    output_name = args.file_name + ".csv" if args.file_name is not None else args.input + "_" + str(args.k) + "_mer.csv"
    kmer_count_dataframe(args.k, df).to_csv(output_name, index=False)

def handle_cli_input():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Query
    parser_query = subparsers.add_parser('query', help='Run a query on the repeatsdb API')
    parser_query.add_argument('query_string', help='Una stringa come argomento', type=str, nargs='+')
    parser_query.add_argument('-o', '--output', dest='output_format', choices=['json', 'csv'],
                              help='Output format (default: csv)', default='csv')
    parser_query.add_argument('-n', '--name', dest='file_name', help='File name (default: output)', default='output')
    parser_query.add_argument('-r', '--regions', dest='merge_regions', action='store_true',
                              help='Merge regions (default: false)')
    # Kmer count
    parser_kmer = subparsers.add_parser('kmer', help='Count kmers in a dataset')
    parser_kmer.add_argument('input', help='Input file name', type=str)
    parser_kmer.add_argument('k', help='Kmer length', type=int, nargs='?', default=0)
    parser_kmer.add_argument('-n', '--name', dest='file_name', help='File name (default: input_k_mer)', default=None,
                             type=str)
    try:
        while True:

            user_input = input("Write a command below (exit or Ctrl + d to stop the cli):\n").strip()

            if user_input.lower() == 'exit':
                break

            args = parser.parse_args(user_input.split())

            try:
                start = time.time()
                match args.command:
                    case 'query':
                        handle_query(args)
                    case 'kmer':
                        handle_kmer(args)
                    case _:
                        print("Invalid command")
                elapsed = time.time() - start
                print(f"Elapsed time: {elapsed:.5f} seconds")
            except ValueError as e:
                print(e)

    except EOFError:
        print("\nExiting")
