import streamlit as st
import requests
import json
import re

BOOKMAKERS = [
    "ggbet",
    "parimatch",
    "betboom",
    "spinbetter",
    "pinnacle",
    "fonbet",
    "ray4bet",
    "bet365"
]

st.set_page_config(page_title="Bets Comparator", page_icon="🎮", layout="wide")

st.markdown("""
<style>
    .title {
        font-size: 2.5rem;
        font-weight: bold;
        color: #ff6b35;
        margin-bottom: 1rem;
    }
    .match-info {
        background: linear-gradient(135deg, #1e1e2e 0%, #2d2d44 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
    }
    .bookmaker-card {
        background: #1e1e2e;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    .best-odd {
        background: linear-gradient(135deg, #00c853 0%, #00e676 100%);
        color: #000;
        padding: 0.3rem 0.8rem;
        border-radius: 4px;
        font-weight: bold;
    }
    .vs {
        font-size: 1.5rem;
        font-weight: bold;
        color: #ff6b35;
    }
    .stTextInput > div > div > input {
        background: #1e1e2e;
        border: 2px solid #3d3d5c;
    }
    .stTextInput > div > div > input:focus {
        border-color: #ff6b35;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<p class="title">🎮 Betting Odds Comparator</p>', unsafe_allow_html=True)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
}

def parse_hawk(url):
    try:
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        html = response.text
        
        match = re.search(r'data-page="({.*?})"', html)
        if not match:
            return [], "Unknown Tournament"
        
        json_str = match.group(1)
        json_str = json_str.replace('&quot;', '"')
        
        page_data = json.loads(json_str)
        series_data = page_data.get('props', {}).get('seriesPageData', {})
        
        if series_data:
            team1_data = series_data.get('team1', {})
            team2_data = series_data.get('team2', {})
            
            team1_name = team1_data.get('name', '')
            team2_name = team2_data.get('name', '')
            
            championship = series_data.get('championship', {})
            tournament = championship.get('name', 'Unknown Tournament')
            
            if team1_name and team2_name:
                return [team1_name, team2_name], tournament
        
        return [], "Unknown Tournament"
        
    except Exception as e:
        return [], f"Error: {str(e)}"

def get_odds(teams, match_url=None):
    from selenium_parser import get_all_odds as get_odds_internal
    return get_odds_internal(teams, match_url=match_url)

col1, col2 = st.columns([2, 1])

with col1:
    match_url = st.text_input("🔗 Hawk Live Match URL", placeholder="https://hawk.live/dota-2/matches/...")

with col2:
    st.write("")
    st.write("")
    refresh_btn = st.button("🔄 Parse Match", use_container_width=True)

if match_url:
    teams, tournament = parse_hawk(match_url)
    
    if teams and len(teams) >= 2:
        team1, team2 = teams[0], teams[1]
        
        st.markdown(f"""
        <div class="match-info">
            <h2 style="margin: 0; color: #fff;">{team1} <span class="vs">VS</span> {team2}</h2>
            <p style="margin: 0.5rem 0 0 0; color: #888;">🏆 {tournament}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📊 Коэффициенты на победу в серии")
        
        odds = get_odds(teams, match_url=match_url)
        
        best_team1 = max(odds.items(), key=lambda x: x[1]['team1'])
        best_team2 = max(odds.items(), key=lambda x: x[1]['team2'])
        
        header_col1, header_col2, header_col3 = st.columns([2, 1, 1])
        with header_col1:
            st.markdown("**Букмекер**")
        with header_col2:
            st.markdown(f"**{team1}**")
        with header_col3:
            st.markdown(f"**{team2}**")
        
        for bookmaker in BOOKMAKERS:
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"**{bookmaker}**")
            
            with col2:
                od = odds[bookmaker]['team1']
                is_best = bookmaker == best_team1[0]
                if is_best:
                    st.markdown(f'<span class="best-odd">{od}</span>', unsafe_allow_html=True)
                else:
                    st.write(str(od))
            
            with col3:
                od = odds[bookmaker]['team2']
                is_best = bookmaker == best_team2[0]
                if is_best:
                    st.markdown(f'<span class="best-odd">{od}</span>', unsafe_allow_html=True)
                else:
                    st.write(str(od))
        
        st.divider()
        st.info("💡 Коэффициенты взяты из API hawk.live")
        
    else:
        st.error(f"Не удалось распознать команды: {tournament}")
else:
    st.info("👆 Введите ссылку на матч с Hawk Live, чтобы начать")
    
    st.subheader("📋 Список букмекеров")
    for bm in BOOKMAKERS:
        st.write(f"• {bm}")