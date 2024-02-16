import argparse
import time

from controller import run_query, run_kmer_count


def handle_query(args):
    run_query("".join(args.query_string), args.file_name, args.merge_regions, args.n_threads)


def handle_kmer(args):
    run_kmer_count(args.input, args.k, args.file_name, args.n_threads)

def handle_command(args):
    try:
        start = time.time()
        match args.command:
            case 'query':
                handle_query(args)
            case 'kmer':
                handle_kmer(args)
            case 'exit':
                print("Exiting")
                exit(0)
            case _:
                print("Invalid command")
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.5f} seconds")
    except ValueError as e:
        print(e)

def handle_cli_input():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Query
    parser_query = subparsers.add_parser('query', help='Run a query on the repeatsdb API')
    parser_query.add_argument('query_string', help='Query string for repeatsdb api', type=str, nargs='+')
    parser_query.add_argument('-n', '--name', dest='file_name', help='File name (default: output)', default='output')
    parser_query.add_argument('-r', '--regions', dest='merge_regions', action='store_true',
                              help='Merge regions (default: false)')
    parser_query.add_argument('-t', '--threads', dest='n_threads', help='Number of threads (default: 5)', type=int,
                              default=5)
    # Kmer count
    parser_kmer = subparsers.add_parser('kmer', help='Count kmers in a dataset')
    parser_kmer.add_argument('input', help='Input file name', type=str)
    parser_kmer.add_argument('k', help='Kmer length', type=int, nargs='?', default=0)
    parser_kmer.add_argument('-n', '--name', dest='file_name', help='File name (default: input_k_mer)', default=None,
                             type=str)
    parser_kmer.add_argument('-t', '--threads', dest='n_threads', help='Number of threads (default: 5)', type=int,
                             default=5)

    # Exit
    subparsers.add_parser('exit', help='Exit the cli')
    command_queue = []
    try:
        while True:
            if not command_queue:
                user_input = input("Write a command below (exit to stop the cli):\n").strip()
                commands = user_input.split("&&")
                args = parser.parse_args(commands[0].split())
                command_queue = commands[1:]
            else:
                args = parser.parse_args(command_queue.pop(0).split())
            handle_command(args)

    except EOFError:
        print("\nExiting")
