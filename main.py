import sys


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "-c":
        from app.cli import handle_cli_input
        handle_cli_input()
    else:
        from gui.gui import run
        run()


if __name__ == '__main__':
    main()
