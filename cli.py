import argparse
from api import query_api
import re
from data_preprocessing import preprocess_from_json

COLON_PATTERN = re.compile(r'^(?:[^:]+:)+[^:]+$')


def check_query_string(query_string):
    if not COLON_PATTERN.match(query_string):
        raise ValueError("Query string must be in the form of \"field:value\".")


def handle_query(args):
    q = "".join(args.query_string)
    check_query_string(q)
    q += "%2Breviewed:true&show=entries"
    preprocess_from_json(query_api("query=" + q), args.merge_regions, args.file_name, args.output_format)


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
    try:
        while True:

            user_input = input("Write a command below (exit or Ctrl + d to stop the cli):\n").strip()

            if user_input.lower() == 'exit':
                break

            args = parser.parse_args(user_input.split())

            try:
                if args.command == 'query':
                    handle_query(args)
                else:
                    print("Unknown command.")
            except ValueError as e:
                print(e)

    except EOFError:
        print("\nRilevato EOF. Uscita.")
