import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "data/lnb nowe.csv"
    
    try:
        # NAPRAWIA zepsuty CSV
        df = pd.read_csv(data_path, on_bad_lines='skip')
        print(f"✓ Wczytano {len(df)} graczy z LNB")
        print("Kolumn:", list(df.columns))
    except Exception as e:
        print(f"✗ Błąd CSV: {e}")
        df = pd.DataFrame({"message": ["Błąd CSV"]})

    df.to_csv("realgm_3d_players_weekly.csv", index=False)
    print("✓ Zapisano realgm_3d_players_weekly.csv")

if __name__ == "__main__":
    main()
