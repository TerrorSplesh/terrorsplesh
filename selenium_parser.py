import requests
import json
import re

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
}

def parse_hawk_odds(match_url):
    try:
        response = requests.get(match_url, headers=HEADERS, timeout=10)
        
        if response.status_code != 200:
            return {}
        
        html = response.text
        
        match = re.search(r'data-page="({.*?})"', html)
        if not match:
            return {}
        
        json_str = match.group(1)
        json_str = json_str.replace('&quot;', '"')
        
        page_data = json.loads(json_str)
        
        series_data = page_data.get('props', {}).get('seriesPageData', {})
        
        if not series_data:
            return {}
        
        all_odds = {}
        
        matches = series_data.get('matches', [])
        
        for match in matches:
            odds_bundles = match.get('oddsBundles', [])
            
            for bundle in odds_bundles:
                provider = bundle.get('oddsProviderCodeName', '')
                is_team1_first = bundle.get('isTeam1First', True)
                odds_list = bundle.get('odds', [])
                
                for odd_item in odds_list:
                    t1_raw = odd_item.get('firstTeamWin')
                    t2_raw = odd_item.get('secondTeamWin')
                    
                    if t1_raw and t2_raw:
                        if is_team1_first:
                            t1_odd, t2_odd = t1_raw, t2_raw
                        else:
                            t1_odd, t2_odd = t2_raw, t1_raw
                        
                        if provider == 'ggbet':
                            all_odds['ggbet'] = {'team1': t1_odd, 'team2': t2_odd}
                        elif provider == 'parimatch':
                            all_odds['parimatch'] = {'team1': t1_odd, 'team2': t2_odd}
                        elif provider == 'betboom':
                            all_odds['betboom'] = {'team1': t1_odd, 'team2': t2_odd}
                        elif provider == 'spin-better':
                            all_odds['spinbetter'] = {'team1': t1_odd, 'team2': t2_odd}
                        
                        break
        
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