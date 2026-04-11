from flask import Flask, render_template_string, jsonify, request
import requests
import json
import re

app = Flask(__name__)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Cache-Control': 'no-cache',
}

def parse_hawk(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html = response.text
        
        match = re.search(r'data-page="({.*?})"', html)
        if not match:
            return {"teams": [], "tournament": "Unknown"}
        
        json_str = match.group(1).replace('&quot;', '"')
        page_data = json.loads(json_str)
        series_data = page_data.get('props', {}).get('seriesPageData', {})
        
        if series_data:
            team1_data = series_data.get('team1', {})
            team2_data = series_data.get('team2', {})
            championship = series_data.get('championship', {})
            
            return {
                "teams": [team1_data.get('name', ''), team2_data.get('name', '')],
                "tournament": championship.get('name', 'Unknown')
            }
        
        return {"teams": [], "tournament": "Unknown"}
    except:
        return {"teams": [], "tournament": "Error"}

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
                        t1_odd = t1_raw if is_team1_first else t2_raw
                        t2_odd = t2_raw if is_team1_first else t1_raw
                        
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
        .container { max-width: 800px; margin: 0 auto; }
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
        table { width: 100%; border-collapse: collapse; }
        th, td {
            padding: 15px;
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
        .loading { opacity: 0.5; }
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 2px solid #ff6b35;
            border-top: 2px solid transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 10px;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
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
            </div>
            
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
    teams_data = parse_hawk(match_url) if match_url else {"teams": [], "tournament": ""}
    odds = get_odds(match_url) if match_url else {}
    
    return render_template_string(HTML, 
        match_url=match_url,
        teams=teams_data.get('teams', []),
        tournament=teams_data.get('tournament', ''),
        odds=odds,
        bookmakers=BOOKMAKERS
    )

@app.route('/api/odds')
def api_odds():
    from datetime import datetime
    
    match_url = request.args.get('url', '')
    if not match_url:
        return jsonify({"error": "No URL"})
    
    teams_data = parse_hawk(match_url)
    odds = get_odds(match_url)
    
    return jsonify({
        "teams": teams_data.get('teams', []),
        "tournament": teams_data.get('tournament', ''),
        "odds": odds,
        "time": datetime.now().strftime("%H:%M:%S")
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)