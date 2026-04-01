import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "data/lnb_advanced.csv"  # ← POPRAWIONE!

    df = pd.read_csv(
        data_path,
        sep=";",
        header=1,
        on_bad_lines="skip"
    )
    
    print(f"Wczytano {len(df)} graczy z LNB Advanced")
    print("KOLUMNY:", list(df.columns))

    # % na ułamki (usuwa kropki)
    pct_cols = ['TS%', 'eFG%', 'ORB%', 'DRB%', 'TRB%', 'AST%', 'TOV%', 'STL%', 'BLK%', 'USG%']
    for col in pct_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str).str.replace('.', ''), errors='coerce') / 100

    print("Przykładowe TS%:", df['TS%'].head().tolist())

    # FILTROWANIE 3&D (dostosowane do LNB)
    balanced = (
        (df['USG%'].between(0.14, 0.25)) &
        (df['TS%'] >= 0.58) &
        (df['DRB%'] >= 0.10) &
        (df['STL%'] + df['BLK%'] >= 0.015) &
        (df['TOV%'] <= 0.14)
    )

    defensive = (
        (df['USG%'].between(0.10, 0.20)) &
        (df['TS%'] >= 0.56) &
        (df['DRB%'] >= 0.09) &
        (df['STL%'] + df['BLK%'] >= 0.02) &
        (df['TOV%'] <= 0.13)
    )

    df['3D_profile'] = 'none'
    df.loc[balanced, '3D_profile'] = 'balanced'
    df.loc[defensive, '3D_profile'] = 'defensive'

    df['3D_score'] = (
        df['TS%'] * 30 +
        df['USG%'] * 15 +
        df['DRB%'] * 25 +
        (df['STL%'] + df['BLK%']) * 25 -
        df['TOV%'] * 15
    )

    result = df[df['3D_profile'] != 'none'].sort_values('3D_score', ascending=False)
    
    print(f"✓ Znaleziono {len(result)} graczy 3&D")
    print("Top 3:")
    print(result[['Player', 'Team', 'TS%', 'USG%', 'DRB%', '3D_profile', '3D_score']].head(3))

    result.to_csv("lnb_3d_players.csv", index=False)
    print("✓ ZAPISANO lnb_3d_players.csv")

if __name__ == "__main__":
    main()
