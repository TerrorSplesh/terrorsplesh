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

HERO_WIN_RATES = {
    "Phantom Assassin": 50.4, "Spirit Breaker": 51.9, "Queen of Pain": 50.3,
    "Juggernaut": 51.5, "Faceless Void": 53.3, "Lifestealer": 52.5,
    "Doom": 47.0, "Meepo": 49.4, "Invoker": 53.1, "Tidehunter": 51.6,
    "Chen": 50.7, "Keeper of the Light": 49.1, "Earthshaker": 48.6,
    "Axe": 51.2, "Pudge": 52.0, "Bloodseeker": 50.8, "Shadow Fiend": 51.5,
    "Sniper": 52.3, "Morphling": 51.0, "Mirana": 50.5, "Storm Spirit": 52.8,
    "Anti-Mage": 51.2, "Riki": 50.1, "Slark": 51.5, "Sven": 52.0,
    "Wraith King": 50.3, "Kunkka": 49.5, "Huskar": 48.2, "Drow Ranger": 53.5,
    "Lycan": 48.5, "Luna": 51.8, "Dragon Knight": 49.2, "Medusa": 50.5,
    "Timberaw": 50.8, "Batrider": 51.2, "Clinkz": 50.5, "Bounty Hunter": 52.0,
    "Ursa": 51.5, "Techies": 48.0, "Templar Assassin": 52.3, "Nyx Assassin": 53.8,
    "Visage": 47.5, "Silencer": 49.0, "Necrophos": 51.0, "Warlock": 48.5,
    "Beastmaster": 50.8, "Sand King": 51.2, "Enigma": 50.5, "Pugna": 51.0,
    "Dark Seer": 49.8, "Bane": 48.5, "Lich": 52.0, "Lion": 51.5,
    "Witch Doctor": 51.9, "Jakiro": 50.2, "Crystal Maiden": 52.5,
    "Ogre Magi": 51.8, "Skywrath Mage": 50.0, "Ancient Apparition": 51.2,
    "Shadow Shaman": 50.5, "Rubick": 52.0, "Disruptor": 50.8,
    "Oracle": 51.5, "Winter Wyvern": 49.5, "Treant Protector": 48.8,
    "Omniknight": 52.0, "Abaddon": 50.5, "Dazzle": 51.0, "Phoenix": 49.2,
    "Elder Titan": 48.5, "Legion Commander": 52.3, "Magnus": 50.8,
    "Timbersaw": 50.5, "Brewmaster": 49.8, "Tusk": 51.2,
    "Chaos Knight": 52.5, "Tremor": 53.0, "Night Stalker": 51.5,
    "Slardar": 51.2, "Gyrocopter": 49.5, "Hoodwink": 52.8,
    "Dawnbreaker": 50.2, "Marci": 51.0, "Ringmaster": 48.5,
    "Void Spirit": 52.5, "Snapfire": 50.8, "Pangolier": 50.5,
    "Grimstroke": 51.2, "Primal Beast": 49.8, "Spectre": 50.5,
    "Weaver": 51.5, "Phantom Lancer": 58.5, "Ember Spirit": 51.0,
    "Leshrac": 48.5, "Death Prophet": 50.5, "Puck": 51.2,
    "Windranger": 50.8, "Zeus": 52.0, "Lina": 51.5,
    "Enchantress": 48.5, "Nature's Prophet": 50.2, "Arc Warden": 49.5,
    "Sniper": 52.3, "Ratt": 50.8, "Brewmaster": 49.8, "Puck": 51.2,
    "Sand King": 51.2, "Necrophos": 51.0, "Razor": 49.5, "Viper": 50.5,
    "Venomancer": 50.0, "Necrophos": 51.0, "Silencer": 49.0,
    "Warlock": 48.5, "Shadow Demon": 49.5, "Dota": 50.0,
}

def get_hero_winrate(hero_name):
    if not hero_name:
        return 50.0
    
    hero_normalized = hero_name.lower().replace(' ', '').replace('_', '').replace('-', '')
    
    for hr_name, wr in HERO_WIN_RATES.items():
        hr_normalized = hr_name.lower().replace(' ', '').replace('_', '').replace('-', '')
        if hero_normalized in hr_normalized or hr_normalized in hero_normalized:
            return wr
    
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

def calculate_team_strength(picks):
    if not picks:
        return 50.0
    
    total = 0
    count = 0
    for hero in picks:
        wr = get_hero_winrate(hero)
        total += wr
        count += 1
    
    return round(total / count, 1) if count > 0 else 50.0

def calculate_advantage(team1_picks, team2_picks):
    if not team1_picks and not team2_picks:
        return 50, 50
    
    team1_strength = calculate_team_strength(team1_picks)
    team2_strength = calculate_team_strength(team2_picks)
    
    diff = team1_strength - team2_strength
    
    team1_adv = 50 + diff
    team2_adv = 50 - diff
    
    team1_adv = max(5, min(95, team1_adv))
    team2_adv = 100 - team1_adv
    
    return team1_adv, team2_adv

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
        .container { max-width: 900px; margin: 0 auto; }
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
            height: 30px;
            border-radius: 15px;
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
                    if (data.team1_advantage && data.team2_advantage) {
                        updateAdvantage(data.team1_advantage, data.team2_advantage);
                    }
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
        
        function updateAdvantage(t1, t2) {
            const bar1 = document.querySelector('.advantage-team1');
            const bar2 = document.querySelector('.advantage-team2');
            if (bar1) {
                bar1.style.width = t1 + '%';
                bar1.textContent = t1 + '%';
            }
            if (bar2) {
                bar2.style.width = t2 + '%';
                bar2.textContent = t2 + '%';
            }
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
    
    team1_adv, team2_adv = calculate_advantage(
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
        team2_advantage=team2_adv
    )

@app.route('/api/odds')
def api_odds():
    match_url = request.args.get('url', '')
    if not match_url:
        return jsonify({"error": "No URL"})
    
    teams_data = parse_hawk(match_url)
    odds = get_odds(match_url)
    
    team1_adv, team2_adv = calculate_advantage(
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
        "time": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
