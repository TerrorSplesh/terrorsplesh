from flask import Flask, render_template_string, jsonify, request
import requests
import json
import re
from datetime import datetime

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control': 'no-cache',
}

HERO_WIN_RATES_PUB = {
    "Phantom Assassin": 50.4, "Spirit Breaker": 51.9, "Queen of Pain": 50.3,
    "Juggernaut": 51.5, "Faceless Void": 53.3, "Lifestealer": 52.5,
    "Doom": 47.0, "Meepo": 49.4, "Invoker": 53.1, "Tidehunter": 51.6,
    "Chen": 50.7, "Keeper of the Light": 49.1, "Earthshaker": 48.6,
    "Axe": 51.2, "Pudge": 52.0, "Bloodseeker": 50.8, "Shadow Fiend": 51.5,
    "Sniper": 52.3, "Morphling": 51.0, "Mirana": 50.5, "Storm Spirit": 52.8,
    "Anti-Mage": 51.2, "Riki": 50.1, "Slark": 51.5, "Sven": 52.0,
    "Wraith King": 50.3, "Kunkka": 49.5, "Huskar": 48.2, "Drow Ranger": 53.5,
    "Lycan": 48.5, "Luna": 51.8, "Dragon Knight": 49.2, "Medusa": 50.5,
    "Batrider": 51.2, "Clinkz": 50.5, "Bounty Hunter": 52.0, "Ursa": 51.5,
    "Templar Assassin": 52.3, "Nyx Assassin": 53.8, "Visage": 47.5,
    "Silencer": 49.0, "Necrophos": 51.0, "Warlock": 48.5, "Beastmaster": 50.8,
    "Sand King": 51.2, "Enigma": 50.5, "Pugna": 51.0, "Dark Seer": 49.8,
    "Lich": 52.0, "Lion": 51.5, "Witch Doctor": 51.9, "Jakiro": 50.2,
    "Crystal Maiden": 52.5, "Ogre Magi": 51.8, "Skywrath Mage": 50.0,
    "Ancient Apparition": 51.2, "Shadow Shaman": 50.5, "Rubick": 52.0,
    "Disruptor": 50.8, "Oracle": 51.5, "Winter Wyvern": 49.5,
    "Treant Protector": 48.8, "Omniknight": 52.0, "Abaddon": 50.5,
    "Dazzle": 51.0, "Phoenix": 49.2, "Elder Titan": 48.5,
    "Legion Commander": 52.3, "Magnus": 50.8, "Timbersaw": 50.5,
    "Brewmaster": 49.8, "Tusk": 51.2, "Chaos Knight": 52.5,
    "Night Stalker": 51.5, "Slardar": 51.2, "Gyrocopter": 49.5,
    "Hoodwink": 52.8, "Dawnbreaker": 50.2, "Marci": 51.0,
    "Void Spirit": 52.5, "Snapfire": 50.8, "Pangolier": 50.5,
    "Grimstroke": 51.2, "Primal Beast": 49.8, "Spectre": 50.5,
    "Weaver": 51.5, "Phantom Lancer": 58.5, "Ember Spirit": 51.0,
    "Leshrac": 48.5, "Death Prophet": 50.5, "Puck": 51.2,
    "Windranger": 50.8, "Zeus": 52.0, "Lina": 51.5,
    "Enchantress": 48.5, "Nature's Prophet": 50.2, "Arc Warden": 49.5,
    "Ratt": 50.8, "Necrophos": 51.0, "Silencer": 49.0,
    "Viper": 50.5, "Venomancer": 50.0, "Shadow Demon": 49.5,
}

HERO_WIN_RATES_PRO = {
    "Phantom Assassin": 48.5, "Spirit Breaker": 53.7, "Queen of Pain": 50.3,
    "Juggernaut": 49.2, "Faceless Void": 52.0, "Lifestealer": 48.0,
    "Doom": 52.5, "Meepo": 54.0, "Invoker": 52.5, "Tidehunter": 53.5,
    "Chen": 56.0, "Keeper of the Light": 55.2, "Earthshaker": 52.8,
    "Axe": 51.0, "Pudge": 45.0, "Bloodseeker": 48.5, "Shadow Fiend": 49.0,
    "Sniper": 47.5, "Morphling": 55.5, "Mirana": 51.2, "Storm Spirit": 53.8,
    "Anti-Mage": 54.0, "Riki": 46.5, "Slark": 50.5, "Sven": 53.0,
    "Wraith King": 51.5, "Kunkka": 52.0, "Huskar": 54.5, "Drow Ranger": 49.0,
    "Lycan": 55.0, "Luna": 48.5, "Dragon Knight": 52.5, "Medusa": 51.0,
    "Batrider": 58.5, "Clinkz": 51.0, "Bounty Hunter": 49.5, "Ursa": 47.0,
    "Templar Assassin": 53.0, "Nyx Assassin": 52.5, "Visage": 54.0,
    "Silencer": 53.0, "Necrophos": 52.0, "Warlock": 55.5, "Beastmaster": 56.0,
    "Sand King": 53.5, "Enigma": 57.0, "Pugna": 49.0, "Dark Seer": 55.5,
    "Lich": 50.5, "Lion": 49.5, "Witch Doctor": 51.0, "Jakiro": 52.0,
    "Crystal Maiden": 47.5, "Ogre Magi": 50.5, "Skywrath Mage": 46.0,
    "Ancient Apparition": 52.5, "Shadow Shaman": 51.0, "Rubick": 54.5,
    "Disruptor": 55.0, "Oracle": 53.5, "Winter Wyvern": 54.0,
    "Treant Protector": 56.5, "Omniknight": 50.0, "Abaddon": 49.0,
    "Dazzle": 51.5, "Phoenix": 55.0, "Elder Titan": 55.5,
    "Legion Commander": 51.0, "Magnus": 56.5, "Timbersaw": 52.5,
    "Brewmaster": 57.0, "Tusk": 52.0, "Chaos Knight": 48.5,
    "Night Stalker": 53.5, "Slardar": 52.0, "Gyrocopter": 51.5,
    "Hoodwink": 50.0, "Dawnbreaker": 52.0, "Marci": 48.0,
    "Void Spirit": 54.5, "Snapfire": 51.0, "Pangolier": 53.0,
    "Grimstroke": 54.0, "Primal Beast": 51.5, "Spectre": 52.5,
    "Weaver": 49.5, "Phantom Lancer": 51.0, "Ember Spirit": 53.0,
    "Leshrac": 54.5, "Death Prophet": 52.5, "Puck": 55.0,
    "Windranger": 52.0, "Zeus": 49.0, "Lina": 50.5,
    "Enchantress": 55.5, "Nature's Prophet": 53.0, "Arc Warden": 56.0,
}

HERO_PRO_PICK_RATE = {
    "Batrider": 15.2, "Visage": 8.5, "Chen": 7.8, "Magnus": 12.5,
    "Dark Seer": 9.2, "Enigma": 6.5, "Rubick": 14.0, "Puck": 11.8,
    "Storm Spirit": 10.5, "Templar Assassin": 9.8, "Ember Spirit": 11.2,
    "Void Spirit": 8.8, "Hoodwink": 7.5, "Monkey King": 10.0,
    "Snapfire": 6.2, "Grimstroke": 9.5, "Pangolier": 8.2,
    "Marci": 5.5, "Dawnbreaker": 7.0, "Primal Beast": 6.8,
    "Winter Wyvern": 8.5, "Oracle": 7.2, "Disruptor": 9.0,
    "Phoenix": 8.0, "Legion Commander": 12.0, "Night Stalker": 7.5,
    "Slardar": 8.8, "Brewmaster": 6.5, "Tusk": 7.8,
    "Sand King": 10.2, "Beastmaster": 5.8, "Nature's Prophet": 9.2,
}

def get_hero_winrate(hero_name, mode='both'):
    if not hero_name:
        return 50.0
    
    hero_normalized = hero_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    def find_match(db):
        for hr_name, wr in db.items():
            hr_normalized = hr_name.lower().replace(' ', '').replace('_', '').replace('-', '')
            if hero_normalized in hr_normalized or hr_normalized in hero_normalized:
                return wr
        return None
    
    if mode == 'pub':
        return find_match(HERO_WIN_RATES_PUB) or 50.0
    elif mode == 'pro':
        return find_match(HERO_WIN_RATES_PRO) or 50.0
    else:
        pub = find_match(HERO_WIN_RATES_PUB) or 50.0
        pro = find_match(HERO_WIN_RATES_PRO) or 50.0
        return (pub + pro) / 2

def get_hero_pro_strength(hero_name):
    if not hero_name:
        return 50.0
    
    hero_normalized = hero_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    for hr_name, wr in HERO_WIN_RATES_PRO.items():
        hr_normalized = hr_name.lower().replace(' ', '').replace('_', '').replace('-', '')
        if hero_normalized in hr_normalized or hr_normalized in hero_normalized:
            pick_rate = HERO_PRO_PICK_RATE.get(hr_name, 5.0)
            return round(wr + (pick_rate * 0.1), 1)
    
    return 50.0

def parse_hawk(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text
        
        match = re.search(r'data-page="({.*?})"', html)
        if not match:
            return {"teams": [], "tournament": "Unknown", "picks": {"team1": [], "team2": []}}
        
        json_str = match.group(1).replace('&quot;', '"')
        page_data = json.loads(json_str)
        series_data = page_data.get('props', {}).get('seriesPageData', {})
        
        team1_picks = []
        team2_picks = []
        
        if series_data:
            team1_data = series_data.get('team1', {})
            team2_data = series_data.get('team2', {})
            championship = series_data.get('championship', {})
            
            matches = series_data.get('matches', [])
            if matches:
                first_match = matches[0]
                picks = first_match.get('picks', [])
                
                for pick in picks:
                    hero_name = pick.get('hero', {}).get('name', '')
                    if hero_name:
                        hero_name = hero_name.replace('npc_dota_hero_', '').replace('_', ' ').title()
                        if pick.get('isRadiant'):
                            team1_picks.append(hero_name)
                        else:
                            team2_picks.append(hero_name)
            
            return {
                "teams": [team1_data.get('name', ''), team2_data.get('name', '')],
                "tournament": championship.get('name', 'Unknown'),
                "picks": {"team1": team1_picks, "team2": team2_picks}
            }
        
        return {"teams": [], "tournament": "Unknown", "picks": {"team1": [], "team2": []}}
    except Exception as e:
        print(f"Parse error: {e}")
        return {"teams": [], "tournament": "Error", "picks": {"team1": [], "team2": []}}

def calculate_team_stats(picks, mode='both'):
    if not picks:
        return {"avg_pub": 50.0, "avg_pro": 50.0, "avg_both": 50.0, "pro_strength": 50.0}
    
    pub_total, pro_total, both_total, pro_strength_total = 0, 0, 0, 0
    count = 0
    
    for hero in picks:
        pub_wr = get_hero_winrate(hero, 'pub')
        pro_wr = get_hero_winrate(hero, 'pro')
        pro_str = get_hero_pro_strength(hero)
        
        pub_total += pub_wr
        pro_total += pro_wr
        both_total += (pub_wr + pro_wr) / 2
        pro_strength_total += pro_str
        count += 1
    
    if count == 0:
        return {"avg_pub": 50.0, "avg_pro": 50.0, "avg_both": 50.0, "pro_strength": 50.0}
    
    return {
        "avg_pub": round(pub_total / count, 1),
        "avg_pro": round(pro_total / count, 1),
        "avg_both": round(both_total / count, 1),
        "pro_strength": round(pro_strength_total / count, 1)
    }

def calculate_advantage(team1_picks, team2_picks):
    if not team1_picks and not team2_picks:
        return 50, 50, {}, {}
    
    t1_stats = calculate_team_stats(team1_picks)
    t2_stats = calculate_team_stats(team2_picks)
    
    diff_pub = t1_stats['avg_pub'] - t2_stats['avg_pub']
    diff_pro = t1_stats['avg_pro'] - t2_stats['avg_pro']
    diff_both = t1_stats['avg_both'] - t2_stats['avg_both']
    diff_strength = t1_stats['pro_strength'] - t2_stats['pro_strength']
    
    combined_diff = (diff_both * 0.4) + (diff_strength * 0.4) + (diff_pro * 0.2)
    
    team1_adv = 50 + combined_diff
    team2_adv = 50 - combined_diff
    
    team1_adv = max(5, min(95, team1_adv))
    team2_adv = 100 - team1_adv
    
    return team1_adv, team2_adv, t1_stats, t2_stats

def get_odds(match_url):
    try:
        response = requests.get(match_url, headers=HEADERS, timeout=10)
        html = response.text
        
        match = re.search(r'data-page="({.*?})"', html)
        if not match:
            return {}
        
        json_str = match.group(1).replace('&quot;', '"')
        page_data = json.loads(json_str)
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
                
                if t1 and t2:
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
            for match in matches:
                odds_bundles = match.get('oddsBundles', [])
                
                for bundle in odds_bundles:
                    provider = bundle.get('oddsProviderCodeName', '')
                    is_team1_first = bundle.get('isTeam1First', True)
                    odds_list = bundle.get('odds', [])
                    
                    valid_odds = None
                    for odd_item in reversed(odds_list):
                        t1_raw = odd_item.get('firstTeamWin')
                        t2_raw = odd_item.get('secondTeamWin')
                        
                        if t1_raw and t2_raw:
                            valid_odds = {
                                'team1': t1_raw if is_team1_first else t2_raw,
                                'team2': t2_raw if is_team1_first else t1_raw
                            }
                            break
                    
                    if valid_odds:
                        if provider == 'ggbet':
                            all_odds['ggbet'] = valid_odds
                        elif provider == 'parimatch':
                            all_odds['parimatch'] = valid_odds
                        elif provider == 'betboom':
                            all_odds['betboom'] = valid_odds
                        elif provider == 'spin-better':
                            all_odds['spinbetter'] = valid_odds
        
        return all_odds
    except:
        return {}

HTML = '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎮 Betting Odds Comparator</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #0d0d0d 0%, #1a1a2e 100%);
            min-height: 100vh;
            color: #fff;
            padding: 20px;
        }
        .container { max-width: 950px; margin: 0 auto; }
        h1 {
            font-size: 2.5rem;
            color: #ff6b35;
            text-align: center;
            margin-bottom: 20px;
        }
        .input-container {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        input[type="text"] {
            flex: 1;
            padding: 15px;
            font-size: 16px;
            border: 2px solid #3d3d5c;
            border-radius: 8px;
            background: #1e1e2e;
            color: #fff;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #ff6b35;
        }
        .match-info {
            background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 20px;
            text-align: center;
        }
        .match-info h2 {
            font-size: 1.8rem;
            margin-bottom: 10px;
        }
        .vs { color: #ff6b35; }
        .tournament { color: #888; font-size: 0.9rem; }
        .picks-info {
            margin-top: 15px;
            padding: 10px;
            background: #252540;
            border-radius: 8px;
            font-size: 0.85rem;
        }
        .pick-hero {
            display: inline-block;
            background: #3d3d5c;
            padding: 3px 8px;
            border-radius: 4px;
            margin: 2px;
            font-size: 0.8rem;
        }
        .advantage-bar {
            display: flex;
            height: 40px;
            border-radius: 20px;
            overflow: hidden;
            margin: 15px 0;
            background: #1e1e2e;
        }
        .advantage-team1 {
            background: linear-gradient(90deg, #ff6b35, #ff8f65);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #fff;
            transition: width 0.5s ease;
        }
        .advantage-team2 {
            background: linear-gradient(90deg, #6366f1, #818cf8);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            color: #fff;
            transition: width 0.5s ease;
        }
        .advantage-label {
            display: flex;
            justify-content: space-between;
            font-size: 0.9rem;
            color: #888;
            margin-bottom: 10px;
        }
        .stats-row {
            display: flex;
            justify-content: space-between;
            gap: 15px;
            margin-bottom: 15px;
        }
        .stat-card {
            flex: 1;
            background: #1e1e2e;
            padding: 10px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-title {
            font-size: 0.75rem;
            color: #888;
            margin-bottom: 5px;
        }
        .stat-value {
            font-size: 1.1rem;
            font-weight: bold;
        }
        .stat-pub { color: #4ade80; }
        .stat-pro { color: #f472b6; }
        .stat-combo { color: #fbbf24; }
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 12px;
            text-align: center;
            border-bottom: 1px solid #3d3d5c;
        }
        th { background: #1e1e2e; }
        .best-odd {
            background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
            color: #000;
            padding: 5px 15px;
            border-radius: 4px;
            font-weight: bold;
        }
        .update-time {
            text-align: center;
            color: #888;
            margin-top: 20px;
            font-size: 0.9rem;
        }
        .method-info {
            background: #252540;
            padding: 10px;
            border-radius: 8px;
            font-size: 0.8rem;
            color: #aaa;
            margin-bottom: 15px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 Betting Odds Comparator</h1>
        
        <div class="input-container">
            <input type="text" id="matchUrl" placeholder="https://hawk.live/dota-2/matches/..." value="{{ match_url }}">
        </div>
        
        <div id="content">
            {% if teams %}
            <div class="match-info">
                <h2>{{ teams[0] }} <span class="vs">VS</span> {{ teams[1] }}</h2>
                <p class="tournament">🏆 {{ tournament }}</p>
                {% if picks.team1 or picks.team2 %}
                <div class="picks-info">
                    <p><strong>{{ teams[0] }}:</strong> {% for hero in picks.team1 %}<span class="pick-hero">{{ hero }}</span>{% endfor %}</p>
                    <p><strong>{{ teams[1] }}:</strong> {% for hero in picks.team2 %}<span class="pick-hero">{{ hero }}</span>{% endfor %}</p>
                </div>
                {% endif %}
            </div>
            
            {% if team1_advantage > 0 or team2_advantage > 0 %}
            <div class="method-info">
                📊 Метод: Pub Winrate (40%) + Pro Winrate (20%) + Pro Strength (40%)
            </div>
            
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Pub WR</div>
                    <div class="stat-value stat-pub">{{ team1_stats.avg_pub }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Pro WR</div>
                    <div class="stat-value stat-pro">{{ team1_stats.avg_pro }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Combo</div>
                    <div class="stat-value stat-combo">{{ team1_stats.avg_both }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[0] }} - Pro Strength</div>
                    <div class="stat-value stat-combo">{{ team1_stats.pro_strength }}%</div>
                </div>
            </div>
            
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Pub WR</div>
                    <div class="stat-value stat-pub">{{ team2_stats.avg_pub }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Pro WR</div>
                    <div class="stat-value stat-pro">{{ team2_stats.avg_pro }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Combo</div>
                    <div class="stat-value stat-combo">{{ team2_stats.avg_both }}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-title">{{ teams[1] }} - Pro Strength</div>
                    <div class="stat-value stat-combo">{{ team2_stats.pro_strength }}%</div>
                </div>
            </div>
            
            <div class="advantage-label">
                <span>{{ teams[0] }} - {{ team1_advantage }}%</span>
                <span>🎯 Перевес пика</span>
                <span>{{ teams[1] }} - {{ team2_advantage }}%</span>
            </div>
            <div class="advantage-bar">
                <div class="advantage-team1" style="width: {{ team1_advantage }}%">{{ team1_advantage }}%</div>
                <div class="advantage-team2" style="width: {{ team2_advantage }}%">{{ team2_advantage }}%</div>
            </div>
            {% endif %}
            
            <table>
                <thead>
                    <tr>
                        <th>Букмекер</th>
                        <th>{{ teams[0] }}</th>
                        <th>{{ teams[1] }}</th>
                    </tr>
                </thead>
                <tbody id="oddsTable">
                    {% for bookmaker in bookmakers %}
                    <tr>
                        <td><strong>{{ bookmaker }}</strong></td>
                        <td class="team1-{{ bookmaker }}">{{ odds.get(bookmaker, {}).get('team1', 'N/A') }}</td>
                        <td class="team2-{{ bookmaker }}">{{ odds.get(bookmaker, {}).get('team2', 'N/A') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
            
            <p class="update-time">🔄 <span id="updateTime">Обновлено</span></p>
            {% else %}
            <p style="text-align: center; color: #888;">👆 Введите ссылку на матч с Hawk Live</p>
            {% endif %}
        </div>
    </div>
    
    <script>
        let url = document.getElementById('matchUrl').value;
        let interval;
        
        if (url) {
            startAutoRefresh();
        }
        
        document.getElementById('matchUrl').addEventListener('change', function() {
            url = this.value;
            if (url) {
                startAutoRefresh();
                window.location.href = '?url=' + encodeURIComponent(url);
            }
        });
        
        function startAutoRefresh() {
            if (interval) clearInterval(interval);
            refreshOdds();
            interval = setInterval(refreshOdds, 3000);
        }
        
        async function refreshOdds() {
            if (!url) return;
            
            try {
                const response = await fetch('/api/odds?url=' + encodeURIComponent(url));
                const data = await response.json();
                
                if (data.odds) {
                    updateOddsTable(data.odds);
                    document.getElementById('updateTime').textContent = '🔄 Обновлено: ' + data.time;
                }
            } catch (e) {
                console.error(e);
            }
        }
        
        function updateOddsTable(odds) {
            const bookmakers = ['ggbet', 'parimatch', 'betboom', 'spinbetter', 'pinnacle', 'fonbet', 'ray4bet', 'bet365'];
            
            bookmakers.forEach(bm => {
                const t1 = odds[bm]?.team1 || 'N/A';
                const t2 = odds[bm]?.team2 || 'N/A';
                
                const el1 = document.querySelector('.team1-' + bm);
                const el2 = document.querySelector('.team2-' + bm);
                
                if (el1) el1.textContent = t1;
                if (el2) el2.textContent = t2;
            });
        }
        
        const urlParams = new URLSearchParams(window.location.search);
        if (urlParams.has('url')) {
            document.getElementById('matchUrl').value = urlParams.get('url');
        }
    </script>
</body>
</html>
'''

BOOKMAKERS = ["ggbet", "parimatch", "betboom", "spinbetter", "pinnacle", "fonbet", "ray4bet", "bet365"]

@app.route('/')
def home():
    match_url = request.args.get('url', '')
    teams_data = parse_hawk(match_url) if match_url else {"teams": [], "tournament": "", "picks": {"team1": [], "team2": []}}
    odds = get_odds(match_url) if match_url else {}
    
    team1_adv, team2_adv, t1_stats, t2_stats = calculate_advantage(
        teams_data.get('picks', {}).get('team1', []),
        teams_data.get('picks', {}).get('team2', [])
    )
    
    return render_template_string(HTML, 
        match_url=match_url,
        teams=teams_data.get('teams', []),
        tournament=teams_data.get('tournament', ''),
        picks=teams_data.get('picks', {'team1': [], 'team2': []}),
        odds=odds,
        bookmakers=BOOKMAKERS,
        team1_advantage=team1_adv,
        team2_advantage=team2_adv,
        team1_stats=t1_stats,
        team2_stats=t2_stats
    )

@app.route('/api/odds')
def api_odds():
    match_url = request.args.get('url', '')
    if not match_url:
        return jsonify({"error": "No URL"})
    
    teams_data = parse_hawk(match_url)
    odds = get_odds(match_url)
    
    team1_adv, team2_adv, t1_stats, t2_stats = calculate_advantage(
        teams_data.get('picks', {}).get('team1', []),
        teams_data.get('picks', {}).get('team2', [])
    )
    
    return jsonify({
        "teams": teams_data.get('teams', []),
        "tournament": teams_data.get('tournament', ''),
        "picks": teams_data.get('picks', {'team1': [], 'team2': []}),
        "odds": odds,
        "team1_advantage": team1_adv,
        "team2_advantage": team2_adv,
        "team1_stats": t1_stats,
        "team2_stats": t2_stats,
        "time": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
