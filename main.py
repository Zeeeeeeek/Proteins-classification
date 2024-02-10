from app.cli import handle_cli_input
import sys
from gui.gui import run
import os

def main():
    if not os.path.exists("../csv"):
        os.makedirs("../csv")
    if not os.path.exists("../kmers"):
        os.makedirs("../kmers")
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        handle_cli_input()
    else:
        run()


if __name__ == '__main__':
    main()
