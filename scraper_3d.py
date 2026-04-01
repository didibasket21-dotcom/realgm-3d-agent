import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "data/lnb nowe.csv"

    try:
        df = pd.read_csv(data_path, sep=";", header=None, on_bad_lines="skip")
        df = df.dropna(axis=1, how="all")
        df = df.loc[:, (df.astype(str).apply(lambda col: col.str.strip()).ne("").any())]

        header = df.iloc[0]
        df = df[1:].copy()
        df.columns = header

        df.columns = [str(c).strip() for c in df.columns]

        if "" in df.columns:
            df = df.drop(columns=[""])

        print(f"Wczytano wierszy: {len(df)}")
        print("KOLUMNY:")
        print(list(df.columns))
        print("PIERWSZE 5 WIERSZY:")
        print(df.head().to_string())

    except Exception as e:
        print(f"BLAD CSV: {e}")
        df = pd.DataFrame({"message": ["Błąd CSV"]})

    df.to_csv("realgm_3d_players_weekly.csv", index=False)
    print("Zapisano realgm_3d_players_weekly.csv")

if __name__ == "__main__":
    main()
