import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "data/Arkusz-2-Tabela 1.csv"

    # Wczytaj zaawansowane statystyki LNB
    df = pd.read_csv(
        data_path,
        sep=";",
        header=1,  # nagłówek w 2. wierszu
        on_bad_lines="skip"
    )
    
    # Usuń pustą pierwszą kolumnę
    if df.columns[0] == '':
        df = df.iloc[:, 1:]
    
    # Konwertuj na liczby (usuwamy kropki z procentów)
    pct_cols = ['TS%', 'eFG%', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%']
    for col in pct_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', ''), errors='coerce') / 100

    print(f"Wczytano {len(df)} graczy z zaawansowanymi statystykami")
    print("Kluczowe kolumny:", ['TS%', 'USG%', 'DRB%', 'STL%', 'BLK%'])

    # FILTROWANIE 3&D z zaawansowanymi statystykami
    balanced_3d = (
        (df['USG%'].between(0.14, 0.22)) &      # Usage 14-22%
        (df['TS%'] >= 0.57) &                   # True Shooting >=57%
        (df['DRB%'] >= 0.12) &                  # Defensive Rebound % >=12%
        (df['STL%'] + df['BLK%'] >= 0.02) &     # Obrona
        (df['TOV%'] <= 0.13)                    # Turnover % <=13%
    )

    defensive_3d = (
        (df['USG%'].between(0.10, 0.18)) &      # Usage 10-18%
        (df['TS%'] >= 0.56) &                   # TS% >=56%
        (df['DRB%'] >= 0.11) &                  # DRB% >=11%
        (df['STL%'] + df['BLK%'] >= 0.025) &    # Więcej obrony
        (df['TOV%'] <= 0.12)                    # Bardzo mało strat
    )

    df['3D_profile'] = 'none'
    df.loc[balanced_3d, '3D_profile'] = 'balanced'
    df.loc[defensive_3d, '3D_profile'] = 'defensive'

    # 3&D Score
    df['3D_score'] = (
        df['TS%'] * 30 +
        df['USG%'] * 20 +
        df['DRB%'] * 25 +
        (df['STL%'] + df['BLK%']) * 30 -
        df['TOV%'] * 20 +
        df['PER'] * 5
    )

    # ZAPIS TYLKO graczy 3&D
    result = df[df['3D_profile'] != 'none'].sort_values('3D_score', ascending=False)

    print(f"✓ Znaleziono {len(result)} graczy 3&D z LNB Advanced Stats")

    result.to_csv("lnb_3d_advanced_players.csv", index=False)
    print("✓ Zapisano lnb_3d_advanced_players.csv")

if __name__ == "__main__":
    main()
