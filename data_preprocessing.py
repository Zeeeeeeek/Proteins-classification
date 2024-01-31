import pandas as pd


def preprocess_from_json(json, units, outputname, format):
    df = pd.DataFrame(json)
    df.to_csv(outputname + ".csv", index=False)


