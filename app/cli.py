import argparse
import time

from app.controller import run_repeatsdb_query, run_kmer_count, run_models_on_kmers


def handle_query(args):
    run_repeatsdb_query(args.query_classes, args.file_name, args.merge_regions, args.n_threads)


def handle_kmer(args):
    run_kmer_count(args.input, args.k, args.file_name)


def handle_models(args):
    if args.max_sample_size_per_level < 1:
        raise ValueError("Error: max_sample_size_per_level must be an integer greater than 0.")
    run_models_on_kmers(args.path, args.level, args.method, args.max_sample_size_per_level, args.k, args.random_state)


def handle_command(args):
    try:
        start = time.time()
        match args.command:
            case 'query':
                handle_query(args)
            case 'kmer':
                handle_kmer(args)
            case 'models':
                handle_models(args)
            case 'exit':
                print("Exiting")
                exit(0)
            case _:
                print("Invalid command")
        elapsed = time.time() - start
        print(f"Elapsed time: {elapsed:.5f} seconds")
    except (ValueError, FileNotFoundError) as e:
        print(e)


def handle_cli_input():
    parser = argparse.ArgumentParser(description="CLI for the repeatsdb API and kmer counting.")
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Query
    parser_query = subparsers.add_parser('query', help='Run a query on the repeatsdb API')
    parser_query.add_argument('query_classes', help='Query string for repeatsdb api', type=str, nargs='+',
                              choices=['2', '3', '4', '5'])
    parser_query.add_argument('-o', '--output', dest='file_name', help='Output file name (default: output)',
                              default='output')
    parser_query.add_argument('-m', '--merge_regions', dest='merge_regions', action='store_true',
                              help='Merge units in regions (default: false)')
    parser_query.add_argument('-t', '--threads', dest='n_threads', help='Number of threads (default: 5)', type=int,
                              default=5)
    # Kmer count
    parser_kmer = subparsers.add_parser('kmer', help='Count kmers in a dataset')
    parser_kmer.add_argument('input', help='Input file name', type=str)
    parser_kmer.add_argument('k', help='Kmer length', type=int, nargs='?', default=0)
    parser_kmer.add_argument('-o', '--output', dest='file_name',
                             help='Output file name (default: \'input_file_name\'_k_mer)',
                             default=None, type=str)

    # Models
    parser_models = subparsers.add_parser('models', help='Run models on kmer dataset')
    parser_models.add_argument('path', help='Path to the dataset', type=str)
    parser_models.add_argument('level', help='Level', type=str, choices=['clan', 'fold', 'class', 'topology'])
    parser_models.add_argument('method', help='Method', type=str, choices=['cluster', 'classifiers'])
    parser_models.add_argument('k', help='Kmer length', type=int)
    parser_models.add_argument('max_sample_size_per_level',
                               help='Max samples for entries with the same specified level', type=int)
    parser_models.add_argument('-r', '--random', dest='random_state', help='Random state (default: 42)', type=int,
                               default=42)

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

    except (EOFError, KeyboardInterrupt):
        print("\nExiting")
        exit(0)
