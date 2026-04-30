import time
import sqlite3
import requests
import pandas as pd
from io import StringIO

# ── Config ───────────────────────────────────────────────────────────────────
SEASON    = 2026
DB_PATH   = "step_1_playoffs.db"
SLEEP_SEC = 3
TABLE_ID  = "team_game_log_adv_post"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Referer": "https://www.basketball-reference.com/",
}

ALL_TEAMS = ["ATL","BOS","BRK","CHO","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK","OKC","ORL","PHI","PHO","POR","SAC","SAS","TOR","UTA","WAS"]

OFF_COLS = ["offensive_four_factors_efg_pct", "offensive_four_factors_tov_pct", "offensive_four_factors_orb_pct", "offensive_four_factors_ft_per_fga"]
DEF_COLS = ["defensive_four_factors_efg_pct", "defensive_four_factors_tov_pct", "defensive_four_factors_orb_pct", "defensive_four_factors_ft_per_fga"]

RENAME = {
    "offensive_four_factors_efg_pct": "efg_pct", "offensive_four_factors_tov_pct": "tov_pct",
    "offensive_four_factors_orb_pct": "orb_pct", "offensive_four_factors_ft_per_fga": "ft_per_fga",
    "defensive_four_factors_efg_pct": "opp_efg_pct", "defensive_four_factors_tov_pct": "opp_tov_pct",
    "defensive_four_factors_orb_pct": "drb_pct", "defensive_four_factors_ft_per_fga": "opp_ft_per_fga",
}

def sanitize(name):
    return name.strip().replace("%", "_pct").replace("/", "_per_").replace(" ", "_").replace("-", "_").lower()

def main():
    conn = sqlite3.connect(DB_PATH)
    print(f"Starting Playoff Scraping to {DB_PATH}...")
    for team in ALL_TEAMS:
        url = f"https://www.basketball-reference.com/teams/{team}/{SEASON}/gamelog-advanced/"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200: continue
            df_list = pd.read_html(StringIO(r.text), attrs={"id": TABLE_ID})
            if not df_list: continue
            df = df_list[0]
            if isinstance(df.columns, pd.MultiIndex):
                df.columns = [" ".join(str(v) for v in col if "Unnamed" not in str(v)).strip() for col in df.columns]
            df.columns = [sanitize(c) for c in df.columns]
            df = df[pd.to_numeric(df.iloc[:, 0], errors="coerce").notna()].copy()
            df = df[[c for c in df.columns if c in (OFF_COLS + DEF_COLS)]].rename(columns=RENAME)
            df.to_sql(f"{team}_playoffs", conn, if_exists="replace", index=False)
            print(f"  ✓ {team} saved.")
            time.sleep(SLEEP_SEC)
        except Exception: continue
    conn.close()
    print("Done.")

if __name__ == "__main__":
    main()
