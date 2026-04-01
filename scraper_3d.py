import pandas as pd
import requests
from urllib.parse import urljoin
import logging
import os

logging.basicConfig(level=logging.INFO)
s = requests.Session()
s.headers["User-Agent"] = "Mozilla/5.0"

# --- LEAGUES (2025) ---
LEAGUES = [
    ("Finland Korisliiga", "/international/league/55/Finnish-Korisliiga/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("Sweden Basketligan", "/international/league/32/Swedish-Basketligan/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("Hungary NBIA", "/international/league/28/Hungarian-NBIA/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("France LNB Pro A", "/international/league/6/French-LNB-Pro-A/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("Germany BBL", "/international/league/7/German-Basketball-Bundesliga/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("Spain LEB Oro", "/international/league/18/Spanish-LEB-Oro/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("Italy LBA", "/international/league/3/Italian-Lega-Basket-Serie-A/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("ABA League", "/international/league/66/ABA-League/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
    ("Belgium BNXT", "/international/league/65/BNXT-League/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),
]

domain = "https://basketball.realgm.com"


def fetch_realgm_league(url_path):
    url = urljoin(domain, url_path)
    logging.info(f"Fetching: {url}")
    try:
        resp = s.get(url, timeout=30)
        resp.raise_for_status()
        tables = pd.read_html(resp.text)
        if not tables:
            return pd.DataFrame()
        df = tables[0]
        return df
    except Exception as e:
        logging.error(f"Fetch error: {e}")
        return pd.DataFrame()


def filter_3d_players(df: pd.DataFrame) -> pd.DataFrame:
    # --- Nazwy kolumn --- #
    usage_col = "Usage%"
    ts_col = "TS%"
    p3p = "3P%"
    p3pa = "3PA"
    mpg = "MPG"
    drb = "DRB"
    drbr = "DREB%"
    pf = "PF"
    tov = "TOV%"
    ast = "AST%"
    stl = "STL"
    blk = "BLK"
    pt = "PTS"

    # --- 1. Profile 3&D BALANCED (Twój obecny) --- #
    cond_bal_usage = df[usage_col].between(14.0, 22.0)
    cond_bal_ts = df[ts_col] >= 57.0
    cond_bal_3p = df[p3p] >= 36.0
    cond_bal_3pa = df[p3pa] >= 2.0
    cond_bal_drb = df[drb] >= 3.0
    cond_bal_pf = df[pf] <= 3.6
    cond_bal_tov = df[tov] <= 8.5
    cond_bal_ast = df[ast] <= 14.0
    cond_bal_def = True
    if stl in df.columns and blk in df.columns:
        df["STL_BLK"] = df[stl] + df[blk]
        cond_bal_def = df["STL_BLK"] >= 0.9

    balanced_mask = (
        cond_bal_usage & cond_bal_ts & cond_bal_3p & cond_bal_3pa & cond_bal_drb
        & cond_bal_pf & cond_bal_tov & cond_bal_ast
    )
    if cond_bal_def is not True:
        balanced_mask &= cond_bal_def

    # --- 2. Profile 3&D DEFENSIVE (nowy) --- #
    cond_def_usage = df[usage_col].between(10.0, 18.0)
    cond_def_ts = df[ts_col] >= 56.0
    cond_def_3p = df[p3p] >= 35.0
    cond_def_3pa = df[p3pa] >= 2.0
    cond_def_drb = df[drb] >= 2.8
    cond_def_drbr = True
    if drbr in df.columns:
        cond_def_drbr = df[drbr] >= 10.0
    cond_def_pf = df[pf] <= 3.3
    cond_def_tov = df[tov] <= 8.0
    cond_def_ast = df[ast] <= 10.0
    cond_def_def = True
    if stl in df.columns and blk in df.columns:
        cond_def_def = df["STL_BLK"] >= 1.2
    cond_def_pts = df[pt] <= 14.0

    defensive_mask = (
        cond_def_usage & cond_def_ts & cond_def_3p & cond_def_3pa & cond_def_drb
        & cond_def_pf & cond_def_tov & cond_def_ast & cond_def_pts
    )
    if cond_def_def is not True:
        defensive_mask &= cond_def_def
    if drbr in df.columns:
        defensive_mask &= cond_def_drbr

    # --- Zaznacz w df, jaki profil spełnia każdy gracz --- #
    df = df.copy()
    df["3D_profile"] = "none"
    df.loc[balanced_mask, "3D_profile"] = "balanced"
    df.loc[defensive_mask, "3D_profile"] = "defensive"
    return df[df["3D_profile"] != "none"].copy()


def main():
    all_frames = []
    for league_name, url_path in LEAGUES:
        df = fetch_realgm_league(url_path)
        if df.empty:
            continue
        df["League"] = league_name
        all_frames.append(df)

    if all_frames:
        final_df = pd.concat(all_frames, ignore_index=True)
        # 1. Zfiltruj po profilach
        final_df = filter_3d_players(final_df)
        # 2. Score 3&D Balanced
        if "Usage%" in final_df.columns:
            final_df["3D_score_balanced"] = (
                0.3 * final_df["Usage%"] +
                0.4 * final_df["TS%"] / 100 +
                0.2 * final_df["3P%"] / 100 +
                0.1 * final_df["DRB"]
            )
        # 3. Score 3&D Defensive
        if "DREB%" in final_df.columns:
            final_df["3D_score_defensive"] = (
                0.2 * final_df["Usage%"] +
                0.2 * final_df["TS%"] / 100 +
                0.2 * final_df["3P%"] / 100 +
                0.2 * final_df["DREB%"] +
                0.15 * final_df["STL"] +
                0.15 * final_df["BLK"] +
                0.05 / (final_df["TOV%"] + 0.1)
            )
        # 4. Posortuj
        final_df = final_df.sort_values("3D_score_balanced", ascending=False)
    else:
        final_df = pd.DataFrame({"message": ["No data found"]})

    final_df.to_csv("realgm_3d_players_weekly.csv", index=False)
    logging.info("CSV saved.")

    # --- WYSLANIE MAILA Z CSV --- #
    try:
        import yagmail

        # Ustawienia maila - ZMIEŃ NA SWOJE!
        GMAIL_LOGIN = "didibasket21@gmail.com"            # Twój Gmail
        GMAIL_APP_PASSWORD = "riac jhxm beqc rczq"    # 16‑znakowy token aplikacyjny
        RECIPIENT_EMAIL = "didibasket21@gmail.com"        # na kogo wysyłasz raport

        yag = yagmail.SMTP(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        yag.send(
            to=RECIPIENT_EMAIL,
            subject="3&D Players Weekly Report – Balanced & Defensive",
            contents="Here is your 3&D players list for this week (balanced + defensive 3&D).",
            attachments="realgm_3d_players_weekly.csv"
        )
        logging.info("Email with CSV sent successfully.")
    except Exception as e:
        logging.warning(f"Failed to send email: {e}")
    # -------------------------------- #


if __name__ == "__main__":
    main()
