from api import repeatsdb_get
from cli import handle_cli_input


def main():
    #json = query_api("query=class:2&reviewed=true&show=entries")
    #pd.DataFrame(json).to_csv("output.csv")
    handle_cli_input()


if __name__ == '__main__':
    main()
