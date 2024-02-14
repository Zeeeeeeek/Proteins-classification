from cli import handle_cli_input
import logging

logging.basicConfig(filename='app.log', level=logging.ERROR, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')


def main():
    try:
        handle_cli_input()
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    main()