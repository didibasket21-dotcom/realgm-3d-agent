import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "data/lnb_advanced.csv"

    df = pd.read_csv(data_path, sep=";", header=1, on_bad_lines="skip")
    
    print(f"Wczytano {len(df)} graczy")
    print("KOLUMNY:", list(df.columns))

    # % na ułamki
    pct_cols = ['TS%', 'eFG%', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%']
    for col in pct
