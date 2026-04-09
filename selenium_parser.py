import requests
from bs4 import BeautifulSoup
import time
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def parse_with_retry(url, retries=2):
    for _ in range(retries):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            print(f"Request error: {e}")
            time.sleep(1)
    return None

def parse_ray4bet(teams):
    team1, team2 = teams[0], teams[1]
    search_url = f"https://ray4bet.com/search?q={team1}+{team2}"
    
    soup = parse_with_retry(search_url)
    if not soup:
        return {"team1": "N/A", "team2": "N/A"}
    
    try:
        match_link = soup.select_one("a[href*='/match/']")
        if match_link:
            match_url = match_link.get('href')
            if not match_url.startswith('http'):
                match_url = "https://ray4bet.com" + match_url
            
            soup = parse_with_retry(match_url)
            if soup:
                odds_elements = soup.select(".odds, .coefficient, [class*='odd']")
                if len(odds_elements) >= 2:
                    return {
                        "team1": odds_elements[0].get_text(strip=True),
                        "team2": odds_elements[1].get_text(strip=True)
                    }
    except Exception as e:
        print(f"Ray4Bet error: {e}")
    
    return {"team1": "N/A", "team2": "N/A"}

def parse_pinnacle(teams):
    search_url = f"https://www.pinnacle.com/search?q={teams[0]}+{teams[1]}"
    
    soup = parse_with_retry(search_url)
    if not soup:
        return {"team1": "N/A", "team2": "N/A"}
    
    try:
        odds_elements = soup.select(".price, .bet-price, [class*='price']")
        if len(odds_elements) >= 2:
            return {
                "team1": odds_elements[0].get_text(strip=True),
                "team2": odds_elements[1].get_text(strip=True)
            }
    except Exception as e:
        print(f"Pinnacle error: {e}")
    
    return {"team1": "N/A", "team2": "N/A"}

def parse_fonbet(teams):
    search_url = f"https://www.fonbet.ru/search/?q={teams[0]}+{teams[1]}"
    
    soup = parse_with_retry(search_url)
    if not soup:
        return {"team1": "N/A", "team2": "N/A"}
    
    try:
        odds_elements = soup.select(".odd, .bet-coefficient, [class*='odd']")
        if len(odds_elements) >= 2:
            return {
                "team1": odds_elements[0].get_text(strip=True),
                "team2": odds_elements[1].get_text(strip=True)
            }
    except Exception as e:
        print(f"Fonbet error: {e}")
    
    return {"team1": "N/A", "team2": "N/A"}

def parse_parimatch(teams):
    search_url = f"https://www.parimatch.ru/search/?q={teams[0]}+{teams[1]}"
    
    soup = parse_with_retry(search_url)
    if not soup:
        return {"team1": "N/A", "team2": "N/A"}
    
    try:
        odds_elements = soup.select(".odd, .coefficient, [class*='odd']")
        if len(odds_elements) >= 2:
            return {
                "team1": odds_elements[0].get_text(strip=True),
                "team2": odds_elements[1].get_text(strip=True)
            }
    except Exception as e:
        print(f"Parimatch error: {e}")
    
    return {"team1": "N/A", "team2": "N/A"}

def parse_betboom(teams):
    search_url = f"https://betboom.ru/search?q={teams[0]}+{teams[1]}"
    
    soup = parse_with_retry(search_url)
    if not soup:
        return {"team1": "N/A", "team2": "N/A"}
    
    try:
        odds_elements = soup.select(".odd, .coefficient")
        if len(odds_elements) >= 2:
            return {
                "team1": odds_elements[0].get_text(strip=True),
                "team2": odds_elements[1].get_text(strip=True)
            }
    except Exception as e:
        print(f"BetBoom error: {e}")
    
    return {"team1": "N/A", "team2": "N/A"}

def parse_bet365(teams):
    return {"team1": "N/A", "team2": "N/A"}

PARSERS = {
    "ray4bet": parse_ray4bet,
    "pinnacle": parse_pinnacle,
    "fonbet": parse_fonbet,
    "parimatch": parse_parimatch,
    "betboom": parse_betboom,
    "bet365": parse_bet365
}

def get_all_odds(teams):
    results = {}
    for name, parser in PARSERS.items():
        results[name] = parser(teams)
    return results
