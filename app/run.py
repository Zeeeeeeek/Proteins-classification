from cli import handle_cli_input

def main():
    try:
        handle_cli_input()
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
