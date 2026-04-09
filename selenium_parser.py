import requests
from bs4 import BeautifulSoup
import time
import re
import random

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cookie': 'CookieConsent=accepted',
}

FREE_PROXIES = []

def fetch_free_proxies():
    global FREE_PROXIES
    try:
        response = requests.get(
            "https://cdn.jsdelivr.net/gh/proxifly/free-proxy-list@main/proxies/protocols/http/data.txt",
            timeout=10
        )
        if response.status_code == 200:
            lines = response.text.strip().split('\n')
            FREE_PROXIES = [f"http://{line.strip()}" for line in lines if line.strip()]
            print(f"Loaded {len(FREE_PROXIES)} free proxies")
    except Exception as e:
        print(f"Failed to fetch proxies: {e}")
        FREE_PROXIES = []

def get_random_proxy():
    if not FREE_PROXIES:
        fetch_free_proxies()
    if FREE_PROXIES:
        return random.choice(FREE_PROXIES)
    return None

def parse_with_proxy(url, proxy=None):
    for attempt in range(3):
        try:
            proxies = {"http": proxy, "https": proxy} if proxy else None
            response = requests.get(url, headers=HEADERS, timeout=10, proxies=proxies)
            if response.status_code == 200:
                return BeautifulSoup(response.content, 'lxml')
        except Exception as e:
            if attempt < 2:
                time.sleep(1)
            else:
                print(f"Request failed: {e}")
    return None

def parse_hawk_odds(match_url):
    soup = parse_with_proxy(match_url)
    if not soup:
        proxy = get_random_proxy()
        if proxy:
            print(f"Trying with proxy: {proxy}")
            soup = parse_with_proxy(match_url, proxy)
    if not soup:
        return parse_hawk_odds_fallback(match_url)
    
    all_odds = {}
    page_text = str(soup)
    
    odd_patterns = [
        r'>\s*(\d+\.\d+)\s*<',
        r'(\d+\.\d+)\s*</a>',
    ]
    
    for pattern in odd_patterns:
        matches = re.findall(pattern, page_text, re.IGNORECASE)
        for m in matches:
            try:
                val = float(m)
                if val > 1.01 and val < 10:
                    if 'team1' not in all_odds:
                        all_odds['team1'] = m
                    elif 'team2' not in all_odds:
                        all_odds['team2'] = m
            except:
                pass
    
    links = soup.select('a[href*="redirectggua.com"]')
    for link in links:
        text = link.get_text(strip=True)
        if text and re.match(r'^\d+\.\d+$', text):
            val = float(text)
            if val > 1.01 and val < 10:
                if 'ggbet1' not in all_odds:
                    all_odds['ggbet1'] = text
                elif 'ggbet2' not in all_odds:
                    all_odds['ggbet2'] = text
    
    return all_odds

def parse_hawk_odds_fallback(match_url):
    try:
        response = requests.get(match_url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(response.content, 'lxml')
        all_odds = {}
        
        odd_elements = soup.select('[class*="odd"], .odds, .coefficient')
        for elem in odd_elements[:4]:
            text = elem.get_text(strip=True)
            if re.match(r'^\d+\.\d+$', text):
                val = float(text)
                if val > 1.01 and val < 10:
                    if 'alt1' not in all_odds:
                        all_odds['alt1'] = text
                    elif 'alt2' not in all_odds:
                        all_odds['alt2'] = text
        
        return all_odds
    except Exception as e:
        print(f"Error: {e}")
        return {}

def get_all_odds(teams=None, match_url=None):
    if match_url:
        odds = parse_hawk_odds(match_url)
        
        team1 = odds.get('team1') or odds.get('ggbet1') or odds.get('alt1') or "N/A"
        team2 = odds.get('team2') or odds.get('ggbet2') or odds.get('alt2') or "N/A"
        
        return {
            "ggbet": {"team1": team1, "team2": team2},
            "parimatch": {"team1": "N/A", "team2": "N/A"},
            "pinnacle": {"team1": "N/A", "team2": "N/A"},
            "betboom": {"team1": "N/A", "team2": "N/A"},
            "fonbet": {"team1": "N/A", "team2": "N/A"},
            "ray4bet": {"team1": "N/A", "team2": "N/A"},
            "bet365": {"team1": "N/A", "team2": "N/A"}
        }
    
    return {
        "ggbet": {"team1": "N/A", "team2": "N/A"},
        "parimatch": {"team1": "N/A", "team2": "N/A"},
        "pinnacle": {"team1": "N/A", "team2": "N/A"},
        "betboom": {"team1": "N/A", "team2": "N/A"},
        "fonbet": {"team1": "N/A", "team2": "N/A"},
        "ray4bet": {"team1": "N/A", "team2": "N/A"},
        "bet365": {"team1": "N/A", "team2": "N/A"}
    }

fetch_free_proxies()
