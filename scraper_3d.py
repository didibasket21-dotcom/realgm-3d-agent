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
    else:
        final_df = pd.DataFrame({"message": ["No data found"]})

    final_df.to_csv("realgm_3d_players_weekly.csv", index=False)
    logging.info("CSV saved.")

    # --- WYSLANIE MAILA Z CSV --- #
    # Uwaga: musisz zainstalować yagmail w GitHub Actions
    try:
        import yagmail

        # Ustawienia maila - ZMIEŃ NA SWOJE!
        GMAIL_LOGIN = "didibasket21@gmail.com"            # Twój Gmail
        GMAIL_APP_PASSWORD = "riac jhxm beqc rczq"    # 16‑znakowy token z App passwords
        RECIPIENT_EMAIL = "didibasket21@gmail.com"        # adres odbiorcy

        # Wysyłka
        yag = yagmail.SMTP(GMAIL_LOGIN, GMAIL_APP_PASSWORD)
        yag.send(
            to=RECIPIENT_EMAIL,
            subject="3&D Players Weekly Report – RealGM",
            contents="Here is your 3&D players list for this week.",
            attachments="realgm_3d_players_weekly.csv"
        )
        logging.info("Email with CSV sent successfully.")
    except Exception as e:
        logging.warning(f"Failed to send email: {e}")
    # -------------------------------- #


if __name__ == "__main__":
    main()
