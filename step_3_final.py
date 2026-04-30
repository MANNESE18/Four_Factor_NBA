import requests
import sqlite3
from bs4 import BeautifulSoup
from datetime import datetime
import pytz

# --- Configuration ---
SPORT = 'basketball_nba'
REGION = 'us'
MARKETS = 'spreads'
ODDS_FORMAT = 'american'
BOOKMAKERS = 'fanduel,draftkings'

def get_model_score(team_name, db_file):
    """Normalizes team names and retrieves the score from the database."""
    name_map = {
        "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BRK",
        "Charlotte Hornets": "CHO", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
        "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
        "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
        "Los Angeles Clippers": "LAC", "LA Clippers": "LAC", "Los Angeles Lakers": "LAL",
        "Memphis Grizzlies": "MEM", "Miami Heat": "MIA", "Milwaukee Bucks": "MIL",
        "Minnesota Timberwolves": "MIN", "New Orleans Pelicans": "NOP", "New York Knicks": "NYK",
        "Oklahoma City Thunder": "OKC", "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI",
        "Phoenix Suns": "PHO", "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC",
        "San Antonio Spurs": "SAS", "Toronto Raptors": "TOR", "Utah Jazz": "UTA",
        "Washington Wizards": "WAS"
    }
    
    search_term = name_map.get(team_name, team_name)

    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        query = "SELECT total_score FROM team_scores WHERE team = ?"
        cursor.execute(query, (search_term,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def scrape_injuries(teams):
    """Scrapes ESPN for Team, Player, and specifically the COMMENT column."""
    url = "https://www.espn.com/nba/injuries"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        resp = requests.get(url, headers=headers)
        soup = BeautifulSoup(resp.content, 'html.parser')
        print(f"\n--- TODAY'S INJURY REPORT ---")
        sections = soup.find_all('div', class_='ResponsiveTable')
        
        for s in sections:
            header = s.find('div', class_='Table__Title')
            # Match the team from the table header
            if header and any(t.lower() in header.text.lower() for t in teams):
                print(f"\n{header.text.upper()}:")
                
                rows = s.find_all('tr', class_='Table__TR')
                for row in rows[1:]:  # Skip the 'NAME, POS, etc' header row
                    cols = row.find_all('td')
                    # Columns: 0:Name, 1:Pos, 2:Return Date, 3:Status, 4:Comment[cite: 6]
                    if len(cols) >= 5:
                        player = cols[0].text.strip()
                        comment = cols[4].text.strip() # Grabbing the 'Comment' info[cite: 6]
                        print(f"  • {player:20} | {comment}")
    except:
        print("Injury report unavailable.")

def run_daily_model():
    api_key = input("Enter Odds API key: ").strip()
    season_input = input("Enter season type (regular / post): ").strip().lower()
    target_db = "step_2_playoffs.db" if "post" in season_input else "step_2_regular.db"

    url = f'https://api.the-odds-api.com/v4/sports/{SPORT}/odds'
    params = {'api_key': api_key, 'regions': REGION, 'markets': MARKETS, 'oddsFormat': ODDS_FORMAT, 'bookmakers': BOOKMAKERS}

    print("\nFetching odds...")
    response = requests.get(url, params=params)
    data = response.json()

    if isinstance(data, dict):
        print(f"API Error: {data.get('message', 'Check key.')}")
        return

    eastern = pytz.timezone('US/Eastern')
    today_str = datetime.now(eastern).strftime('%Y-%m-%d')
    active_games = [g for g in data if datetime.fromisoformat(g['commence_time'].replace('Z', '+00:00')).astimezone(eastern).strftime('%Y-%m-%d') == today_str]

    if not active_games:
        print("No games today.")
        return

    active_teams = [t for g in active_games for t in [g['home_team'], g['away_team']]]
    scrape_injuries(active_teams)

    print(f"\n{'='*60}\n NBA MODEL BOARD - {today_str}\n{'='*60}")
    for game in active_games:
        home, away = game['home_team'], game['away_team']
        line_info = "N/A"
        
        if game['bookmakers']:
            outcomes = game['bookmakers'][0]['markets'][0]['outcomes']
            fav = next((o for o in outcomes if o['point'] < 0), outcomes[0])
            line_info = f"{fav['name']} ({fav['point']})"

        h_score = get_model_score(home, target_db)
        a_score = get_model_score(away, target_db)

        print(f"\n{away} @ {home} | Live Line: {line_info}")
        
        if h_score is not None and a_score is not None:
            if h_score > a_score:
                model_fav_team = home
                model_num = h_score - a_score
            elif a_score > h_score:
                model_fav_team = away
                model_num = a_score - h_score
            else:
                model_fav_team = "Even"
                model_num = 0.0

            # Output Format: Model favors team: +num
            print(f"Model favors {model_fav_team}: +{model_num:.4f}")
        else:
            print(f"Data missing for this matchup in {target_db}.")

if __name__ == "__main__":
    run_daily_model()
