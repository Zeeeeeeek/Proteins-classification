from api import query_api
import pandas as pd


def main():
    json = query_api("query=class:2&reviewed=true&show=entries")
    pd.DataFrame(json).to_csv("output.csv")


if __name__ == '__main__':
    main()
