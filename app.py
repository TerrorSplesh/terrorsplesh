import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
from selenium_parser import get_all_odds

BOOKMAKERS = [
    "parimatch",
    "pinnacle", 
    "betboom",
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

def parse_liquipedia(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'lxml')
        
        teams = []
        team_elements = soup.select('.team-name, .teamcell, .team a')
        for elem in team_elements[:2]:
            team_name = elem.get_text(strip=True)
            if team_name:
                teams.append(team_name)
        
        if len(teams) < 2:
            title = soup.select_one('h1, .page-title')
            if title:
                match_title = title.get_text(strip=True)
                parts = re.split(r' vs | против | - ', match_title, flags=re.IGNORECASE)
                if len(parts) >= 2:
                    teams = [parts[0].strip(), parts[1].strip()]
        
        tournament_elem = soup.select_one('.tournament, .event, .prizepool')
        tournament = tournament_elem.get_text(strip=True) if tournament_elem else "Unknown Tournament"
        
        return teams, tournament
        
    except Exception as e:
        return [], f"Error: {str(e)}"

def get_odds(teams):
    return get_all_odds(teams)

col1, col2 = st.columns([2, 1])

with col1:
    match_url = st.text_input("🔗 Liquipedia Match URL", placeholder="https://liquipedia.net/...")

with col2:
    st.write("")
    st.write("")
    refresh_btn = st.button("🔄 Parse Match", use_container_width=True)

if match_url:
    teams, tournament = parse_liquipedia(match_url)
    
    if teams and len(teams) >= 2:
        team1, team2 = teams[0], teams[1]
        
        st.markdown(f"""
        <div class="match-info">
            <h2 style="margin: 0; color: #fff;">{team1} <span class="vs">VS</span> {team2}</h2>
            <p style="margin: 0.5rem 0 0 0; color: #888;">🏆 {tournament}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.subheader("📊 Коэффициенты на победу в серии")
        
        odds = get_odds(teams)
        
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
        st.info("💡 Коэффициенты получены через Selenium. Если значение N/A - парсинг не нашел данные.")
        
    else:
        st.error(f"Не удалось распознать команды: {tournament}")
else:
    st.info("👆 Введите ссылку на матч с Liquipedia, чтобы начать")
    
    st.subheader("📋 Список букмекеров")
    for bm in BOOKMAKERS:
        st.write(f"• {bm}")
