import argparse
from api import query_api
import pandas as pd
import re

COLON_PATTERN = re.compile(r'^[^:]+:[^:]+$')


def check_query_string(query_string):
    s = re.split(r'[\&\|]', query_string)
    for i in range(len(s)):
        if not COLON_PATTERN.match(s[i]):
            raise ValueError("Query string must be in the form of \"field:value\".")
        s[i] = s[i].split(":")
        if s[i][0] == "class" and (not s[i][1].isnumeric() or int(s[i][1]) < 1 or int(s[i][1]) > 5):
            raise ValueError("Class must be a number between 0 and 5.")


def handle_query(args):
    q = "".join(args.query_string)
    check_query_string(q)
    q += "&reviewed=true&show=entries"
    print("Querying the API with the following query string: {}".format(q))


def handle_cli_input():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(title='commands', dest='command')

    # Query
    parser_query = subparsers.add_parser('query', help='Run a query on the repeatsdb API')
    parser_query.add_argument('query_string', help='Una stringa come argomento', type=str, nargs='+')
    parser_query.add_argument('-o', '--output', dest='output_format', choices=['json', 'csv'],
                              help='Output format (default: csv)', default='csv')
    parser_query.add_argument('-n', '--name', dest='file_name', help='File name (default: output)', default='output')
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
