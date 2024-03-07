import pandas as pd
import numpy as np

def second_place_lambda(x):
    if x.shape[0] > 1:
        return x.sort_values(by="preference").iloc[1]
    else:
        row = x.sort_values(by="preference").iloc[0]
        default_series = pd.Series(index=["url", "exchange", "preference", "class", "type"])
        default_series["url"] = row["url"]
        return default_series

def main():
    df = pd.read_csv("./results/gov_mx_results.csv")
    sorted_df = df.groupby("url", as_index=False)

    dropped_df_first = sorted_df.apply(lambda x : x.sort_values(by="preference").head(1))
    dropped_df_first.to_csv("./results/gov_mx_preference_results.csv", index=False)

    dropped_df_second = sorted_df.apply(lambda x : second_place_lambda(x))
    dropped_df_second.to_csv("./results/gov_mx_second_preference_results.csv", index=False)

if __name__ == "__main__":
    main()