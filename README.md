# NBA Four Factors Analysis & Betting Intelligence

## Overview

This project is an automated data pipeline designed to analyze NBA performance through the lens of the "Four Factors" (Effective Field Goal %, Turnover %, Offensive Rebound %, and Free Throw Rate). Instead of traditional hand-coding, this software was built using an "AI-native" workflow, leveraging **Cursor, Claude, and Gemini** to architect complex scraping and analytical logic. By focusing on high-level system design and tool-assisted execution, the program effectively bridges the gap between raw web data and actionable betting insights.  


## Features

* **Dual-Season Scraping:** Dedicated modules for both Regular Season and Playoff data, pulling advanced game logs directly from Basketball-Reference.  


* **Automated Data Cleaning:** A robust sanitization pipeline that handles multi-index columns, strips whitespace, and formats statistical strings into machine-readable floats.  


* **Four Factors Scoring Model:** A custom weighted algorithm that calculates team strength based on offensive and defensive efficiency across the four critical factors.  


* **Real-Time Injury Integration:** A BeautifulSoup-based scraper that fetches the latest ESPN injury reports, specifically parsing player comments to provide contextual availability.

* **Live Odds Comparison:** Integrates with The Odds API to fetch live spreads from major bookmakers like FanDuel and DraftKings for a direct comparison against the model’s projected favorites.  

## Built With

* **Component:**	Technology / Library
* **Language:**	Python 3.x
* **Development Tools:**	Cursor, Claude 3.5 Sonnet, Gemini 1.5 Pro
* **Data Handling:**	Pandas, SQLite3, NumPy
* **Web Scraping:**	Requests, BeautifulSoup4, LXML
* **Integrations:**	The Odds API, Basketball-Reference, ESPN

## Key Achievements in Code

* **Weighted Analytical Engine:** Implemented a complex scoring formula that weights Effective Field Goal % (40%), Turnover % (25%), Offensive Rebounding % (20%), and Free Throw Rate (15%) for both offense and defense to produce a single "Total Score".  

* **Scalable SQLite Infrastructure:** Designed a multi-step database architecture (Step 1: Raw Scrapes, Step 2: Processed Scores) to ensure data integrity and prevent redundant network requests.  


* **Dynamic Data Normalization:** Developed a `to_decimal` utility and `name_map` dictionary that handles the inconsistencies between web-scraped percentages and API-provided team names, ensuring 100% match rates during the modeling phase.  


* **Time-Zone Aware Automation:** Incorporated `pytz` for US/Eastern time conversion to ensure the model only pulls and analyzes games scheduled for the current calendar day.
