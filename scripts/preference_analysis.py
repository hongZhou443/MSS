import pandas as pd

def main():
    df = pd.read_csv("./data/gov_mx_results.csv")
    print("original")
    print(df.head(5))
    print("sorted")

    sorted_df = df.groupby("url")
    sorted_df.apply(lambda x : x.sort_values(by="preference"))

    dropped_df = sorted_df.apply(lambda x : x.sort_values(by="preference").head(1))
    dropped_df.to_csv("./data/gov_mx_preference_results.csv")
  
if __name__ == "__main__":
    main()