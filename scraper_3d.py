import os
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

def main():
    data_path = "data/lnb nowe.csv"  # ZMIEŃ NA SWOJĄ NAZWĘ

    if os.path.exists(data_path):
        df = pd.read_csv(data_path)
        print(f"✓ Wczytano {len(df)} graczy z {data_path}")
    else:
        df = pd.DataFrame({"message": ["Brak CSV w data/"]})
        print(f"✗ Nie znaleziono {data_path}")

    df.to_csv("realgm_3d_players_weekly.csv", index=False)
    print("✓ Zapisano realgm_3d_players_weekly.csv")

if __name__ == "__main__":
    main()
