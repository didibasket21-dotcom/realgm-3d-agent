{\rtf1\ansi\ansicpg1250\cocoartf2868
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import pandas as pd\
import requests\
from urllib.parse import urljoin\
import time\
import logging\
\
logging.basicConfig(level=logging.INFO)\
s = requests.Session()\
s.headers["User-Agent"] = "Mozilla/5.0"\
\
# --- LEAGUES (2025) ---\
LEAGUES = [\
    ("Finland Korisliiga", "/international/league/55/Finnish-Korisliiga/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("Sweden Basketligan", "/international/league/32/Swedish-Basketligan/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("Hungary NBIA", "/international/league/28/Hungarian-NBIA/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("France LNB Pro A", "/international/league/6/French-LNB-Pro-A/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("Germany BBL", "/international/league/7/German-Basketball-Bundesliga/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("Spain LEB Oro", "/international/league/18/Spanish-LEB-Oro/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("Italy LBA", "/international/league/3/Italian-Lega-Basket-Serie-A/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("ABA League", "/international/league/66/ABA-League/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
    ("Belgium BNXT", "/international/league/65/BNXT-League/stats/2025/Per_Minute/Qualified/All/All/All/asc/1/Regular_Season"),\
]\
\
domain = "https://basketball.realgm.com"\
\
\
def fetch_realgm_league(url_path: str) -> pd.DataFrame:\
    url = urljoin(domain, url_path)\
    logging.info(f"Fetching: \{url\}")\
    try:\
        resp = requests.get(url, timeout=30)\
        resp.raise_for_status()\
        tables = pd.read_html(resp.text, flavor="lxml", attrs=\{"class": "table"\})\
        df = tables[0]  # zwykle pierwsza tabela to gracze\
        if df.shape[0] == 0:\
            return pd.DataFrame()\
        # Pierwszy wiersz to nag\uc0\u322 \'f3wki\
        headers = df.iloc[0]\
        df = df[1:]\
        df.columns = headers\
        return df\
    except Exception as e:\
        logging.error(f"Fetch error: \{e\}")\
        return pd.DataFrame()\
\
\
def filter_3d_players(df: pd.DataFrame) -> pd.DataFrame:\
    # Uwaga: nazwy kolumn poni\uc0\u380 ej musz\u261  pasowa\u263  do RealGM (sprawdzisz po uruchomieniu 1 raz)\
    usage_col = "Usage%"\
    ts_col = "TS%"\
    p3p = "3P%"\
    p3pa = "3PA"\
    mpg = "MPG"\
    drb = "DRB"\
    pf = "PF"\
    tov = "TOV%"\
    ast = "AST%"\
    stl = "STL"\
    blk = "BLK"\
\
    # Je\uc0\u347 li nie ma tych kolumn, przerywamy ten krok dla tej ligi\
    for col in [usage_col, ts_col, p3p, p3pa, mpg, drb, pf, tov, ast]:\
        if col not in df.columns:\
            logging.warning(f"Brak kolumny: \{col\}, pomijam \{len(df)\} graczy dla tej ligi.")\
            return pd.DataFrame()\
\
    # 3&D filter\
    cond_usage = (df[usage_col] >= 14.0) & (df[usage_col] <= 22.0)\
    cond_ts = df[ts_col] >= 57.0\
    cond_3p = df[p3p] >= 36.0\
    cond_3pa = df[p3pa] >= 2.0\
    cond_mpg = df[mpg] >= 15.0\
    cond_drb = df[drb] >= 3.0\
    cond_pf = df[pf] <= 3.6\
    cond_tov = df[tov] <= 8.5\
    cond_ast = df[ast] <= 14.0\
\
    guard = (\
        cond_usage & cond_ts & cond_3p & cond_3pa & cond_drb\
        & cond_mpg & cond_tov & cond_ast & cond_pf\
    )\
\
    if stl in df.columns and blk in df.columns:\
        df["STL_BLK"] = df[stl] + df[blk]\
        guard &= df["STL_BLK"] >= 0.9\
\
    return df[guard].copy() if guard.any() else pd.DataFrame()\
\
\
def main():\
    all_3d_list = []\
    for league_name, url_path in LEAGUES:\
        df = fetch_realgm_league(url_path)\
        if df.empty:\
            continue\
\
        df_3d = filter_3d_players(df)\
        if df_3d.empty:\
            continue\
\
        df_3d["League"] = league_name\
        all_3d_list.append(df_3d)\
        logging.info(f"\{league_name\}: \{len(df_3d)\} 3&D players")\
\
    if all_3d_list:\
        final_df = pd.concat(all_3d_list, ignore_index=True)\
        final_df.to_csv("realgm_3d_players_weekly.csv", index=False)\
        logging.info(f"Saved \{len(final_df)\} 3&D players.")\
    else:\
        logging.info("No 3&D players found.")\
\
\
if __name__ == "__main__":\
    main()\
}