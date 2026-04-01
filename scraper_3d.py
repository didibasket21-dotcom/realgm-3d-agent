import pandas as pd
import logging
import numpy as np

logging.basicConfig(level=logging.INFO)

def filter_3d_players(df):
    # Twój CSV ma: 3PM, 3PA, 3P%, DRB, SPG, BPG, TOV, PF
    df = df.copy()
    
    # Konwertuj na numeryczne (usuwamy kropki)
    for col in ['3P%', 'FG%', 'FT%']:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('.', '').astype(float) / 100

    for col in ['3PM', '3PA', 'FGM', 'FGA', 'FTM', 'FTA', 'ORB', 'DRB', 'RPG', 'APG', 'SPG', 'BPG', 'TOV', 'PF', 'MPG', 'PPG']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # 3&D BALANCED
    balanced = (
        (df['3PA'] >= 3.0) &
        (df['3P%'] >= 0.35) &
        (df['DRB'] >= 2.8) &
        (df['SPG'] + df['BPG'] >= 1.0) &
        (df['TOV'] <= 3.0) &
        (df['PF'] <= 2.8)
    )

    # 3&D DEFENSIVE
    defensive = (
        (df['3PA'] >= 2.5) &
        (df['3P%'] >= 0.34) &
        (df['DRB'] >= 2.5) &
        (df['SPG'] + df['BPG'] >= 1.2) &
        (df['TOV'] <= 2.5) &
        (df['PF'] <= 2.5)
    )

    df['3D_profile'] = 'none'
    df.loc[balanced, '3D_profile'] = 'balanced'
    df.loc[defensive, '3D_profile'] = 'defensive'

    # Score
    df['3D_score_balanced'] = (
        df['3P%'] * 30 +
        df['DRB'] * 10 +
        (df['SPG'] + df['BPG']) * 20 -
        df['TOV'] * 5
    )

    df['3D_score_defensive'] = (
        df['3P%'] * 25 +
        df['DRB'] * 15 +
        (df['SPG'] + df['BPG']) * 25 -
        df['TOV'] * 8
    )

    return df[df['3D_profile'] != 'none'].sort_values('3D_score_balanced', ascending=False)

def main():
    data_path = "data/lnb nowe.csv"

    try:
        df = pd.read_csv(
            data_path,
            sep=";",
            header=None,
            names=[
                "empty", "#", "Player", "Team", "GP", "MPG", "PPG",
                "FGM", "FGA", "FG%", "3PM", "3PA", "3P%",
                "FTM", "FTA", "FT%", "ORB", "DRB", "RPG",
                "APG", "SPG", "BPG", "TOV", "PF"
            ],
            on_bad_lines="skip"
        )

        df = df.iloc[2:].copy()
        df = df.drop(columns=["empty"], errors="ignore")

        print(f"Wczytano {len(df)} graczy z LNB")

        final_df = filter_3d_players(df)
        print(f"Znalezione 3&D graczy: {len(final_df)}")

        final_df.to_csv("realgm_3d_players_weekly.csv", index=False)
        print("✓ Zapisano realgm_3d_players_weekly.csv")

    except Exception as e:
        print(f"BLAD: {e}")
        final_df = pd.DataFrame({"message": ["Błąd"]})
        final_df.to_csv("realgm_3d_players_weekly.csv", index=False)

if __name__ == "__main__":
    main()
