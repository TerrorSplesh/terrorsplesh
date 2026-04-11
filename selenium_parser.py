import requests
from bs4 import BeautifulSoup
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def parse_hawk_odds(match_url):
    try:
        response = requests.get(match_url, headers=HEADERS, timeout=15)
        if response.status_code != 200:
            return {}
        
        soup = BeautifulSoup(response.content, 'lxml')
        
        script_tag = soup.find('script', {'data-page': True})
        if not script_tag:
            return {}
        
        data_attr = script_tag.get('data-page')
        if not data_attr:
            return {}
        
        page_data = json.loads(data_attr)
        
        series_data = page_data.get('props', {}).get('seriesPageData', {})
        
        if not series_data:
            return {}
        
        all_odds = {}
        
        moneylines = series_data.get('moneylines', [])
        if moneylines:
            for ml in moneylines:
                provider = ml.get('oddsProviderCodeName', '')
                t1 = ml.get('team1WinOdds', '')
                t2 = ml.get('team2WinOdds', '')
                
                if provider == 'ggbet':
                    all_odds['ggbet'] = {'team1': t1, 'team2': t2}
                elif provider == 'parimatch':
                    all_odds['parimatch'] = {'team1': t1, 'team2': t2}
                elif provider == 'betboom':
                    all_odds['betboom'] = {'team1': t1, 'team2': t2}
                elif provider == 'spin-better':
                    all_odds['spinbetter'] = {'team1': t1, 'team2': t2}
        
        if not all_odds:
            matches = series_data.get('matches', [])
            if matches:
                first_match = matches[0]
                odds_bundles = first_match.get('oddsBundles', [])
                
                for bundle in odds_bundles:
                    provider = bundle.get('oddsProviderCodeName', '')
                    is_team1_first = bundle.get('isTeam1First', True)
                    odds_list = bundle.get('odds', [])
                    
                    if odds_list:
                        first_odds = odds_list[0]
                        t1_raw = first_odds.get('firstTeamWin', '')
                        t2_raw = first_odds.get('secondTeamWin', '')
                        
                        if is_team1_first:
                            t1, t2 = t1_raw, t2_raw
                        else:
                            t2, t1 = t1_raw, t2_raw
                        
                        if provider == 'ggbet':
                            all_odds['ggbet'] = {'team1': t1, 'team2': t2}
                        elif provider == 'parimatch':
                            all_odds['parimatch'] = {'team1': t1, 'team2': t2}
                        elif provider == 'betboom':
                            all_odds['betboom'] = {'team1': t1, 'team2': t2}
                        elif provider == 'spin-better':
                            all_odds['spinbetter'] = {'team1': t1, 'team2': t2}
        
        return all_odds
        
    except Exception as e:
        print(f"Error parsing hawk: {e}")
        return {}

def get_all_odds(teams=None, match_url=None):
    if match_url:
        odds = parse_hawk_odds(match_url)
        
        return {
            "ggbet": odds.get('ggbet', {"team1": "N/A", "team2": "N/A"}),
            "parimatch": odds.get('parimatch', {"team1": "N/A", "team2": "N/A"}),
            "betboom": odds.get('betboom', {"team1": "N/A", "team2": "N/A"}),
            "spinbetter": odds.get('spinbetter', {"team1": "N/A", "team2": "N/A"}),
            "pinnacle": {"team1": "N/A", "team2": "N/A"},
            "fonbet": {"team1": "N/A", "team2": "N/A"},
            "ray4bet": {"team1": "N/A", "team2": "N/A"},
            "bet365": {"team1": "N/A", "team2": "N/A"}
        }
    
    return {
        "ggbet": {"team1": "N/A", "team2": "N/A"},
        "parimatch": {"team1": "N/A", "team2": "N/A"},
        "betboom": {"team1": "N/A", "team2": "N/A"},
        "spinbetter": {"team1": "N/A", "team2": "N/A"},
        "pinnacle": {"team1": "N/A", "team2": "N/A"},
        "fonbet": {"team1": "N/A", "team2": "N/A"},
        "ray4bet": {"team1": "N/A", "team2": "N/A"},
        "bet365": {"team1": "N/A", "team2": "N/A"}
    }
