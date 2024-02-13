import os

from app.cli import handle_cli_input


def main():
    if not os.path.exists("../csv"):
        os.makedirs("../csv")
    if not os.path.exists("../kmers"):
        os.makedirs("../kmers")
    handle_cli_input()


if __name__ == '__main__':
    main()