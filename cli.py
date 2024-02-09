import argparse
import pandas as pd
import time

from kmer import multithread_kmer_count_df
from controller import run_query, run_kmer_count


def handle_query(args):
    run_query("".join(args.query_string), args.file_name, args.merge_regions)


def handle_kmer(args):
    run_kmer_count(args.input, args.k, args.file_name)

def handle_cli_input():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Query
    parser_query = subparsers.add_parser('query', help='Run a query on the repeatsdb API')
    parser_query.add_argument('query_string', help='Una stringa come argomento', type=str, nargs='+')
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

            user_input = input("Write a command below (exit to stop the cli):\n").strip()

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
