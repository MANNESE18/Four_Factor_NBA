import sqlite3
import pandas as pd

IN_DB   = "step_1_regular.db"
OUT_DB  = "step_2_regular.db"
OUT_TBL = "team_scores"

ALL_TEAMS = ["ATL","BOS","BRK","CHO","CHI","CLE","DAL","DEN","DET","GSW","HOU","IND","LAC","LAL","MEM","MIA","MIL","MIN","NOP","NYK","OKC","ORL","PHI","PHO","POR","SAC","SAS","TOR","UTA","WAS"]

def to_decimal(series):
    s = pd.to_numeric(series, errors="coerce")
    return s.where(s <= 1, s / 100)

def main():
    in_conn = sqlite3.connect(IN_DB)
    out_conn = sqlite3.connect(OUT_DB)
    results = []

    for team in ALL_TEAMS:
        try:
            df = pd.read_sql(f"SELECT * FROM {team}_regular", in_conn)
            avgs = {col: to_decimal(df[col]).mean() for col in df.columns if col != 'team'}
            
            off = (avgs["efg_pct"] * 0.40 + (1 - avgs["tov_pct"]) * 0.25 + avgs["orb_pct"] * 0.20 + avgs["ft_per_fga"] * 0.15)
            deff = ((1 - avgs["opp_efg_pct"]) * 0.40 + avgs["opp_tov_pct"] * 0.25 + avgs["drb_pct"] * 0.20 + (1 - avgs["opp_ft_per_fga"]) * 0.15)
            
            results.append({"team": team, "total_score": round(off + deff, 4)})
        except: continue

    if results:
        pd.DataFrame(results).to_sql(OUT_TBL, out_conn, if_exists="replace", index=False)
        print(f"Regular season scores saved to {OUT_DB}")
    in_conn.close()
    out_conn.close()

if __name__ == "__main__":
    main()
