import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "lnb_advanced.csv"  # ← dokładna nazwa z Twoim plikiem

    df = pd.read_csv(
        data_path,
        sep=";",
        header=1,
        on_bad_lines="skip"
    )
    
    # Usuń pustą kolumnę
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    
    # Nazwij kolumny
    df.columns = [
        'Rank', 'Player', 'Team', 'TS%', 'eFG%', 'Total_S%', 'ORB%', 'DRB%', 'TRB%', 
        'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%', 'PPR', 'PPS', 'ORtg', 'DRtg', 
        'eDiff', 'FIC', 'PER'
    ]

    # % na ułamki
    pct_cols = ['TS%', 'eFG%', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%']
    for col in pct_cols:
        if col in df.columns:
            df[col]
