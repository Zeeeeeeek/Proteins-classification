import pandas as pd


def differentiate_units_ids(df):
    output_df = df.copy()
    counter = -1
    previous_id = df.iloc[0]["repeatsdb_id"]
    for index, row in df.iterrows():
        if previous_id == row["repeatsdb_id"]:
            counter += 1
        else:
            counter = 0
            previous_id = row["repeatsdb_id"]
        output_df.at[index, "repeatsdb_id"] = row["repeatsdb_id"] + "_" + str(counter)
    return output_df


def integrate_regions(df):
    grouped = df.groupby(["region_id"])
    output_df = pd.DataFrame()
    difference_columns = df.columns.difference(["region_id", "start", "end", "type"])
    for region_id, group in grouped:
        r = region_id[0].split("_")
        row = {
            "region_id": region_id[0],
            "start": r[1],
            "end": r[2],
            "type": group["type"].tolist()
        }
        for col in difference_columns:
            row[col] = group[col].iloc[0]
        output_df = pd.concat([output_df, pd.DataFrame([row])], ignore_index=True)
    return output_df


def preprocess_from_json(json, regions, outputname, format):
    df = integrate_regions(pd.DataFrame(json)) if regions else differentiate_units_ids(pd.DataFrame(json))
    if format == "csv":
        df.to_csv(outputname + ".csv", index=False)
