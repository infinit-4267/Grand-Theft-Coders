import streamlit as st
import random
import json
import os
import string
import base64
from PIL import Image, ImageDraw
import pandas as pd
import streamlit.components.v1 as components
from datetime import date

# 1. Page Configuration
st.set_page_config(page_title="Vice City Reputation Engine", layout="wide")

# --- DATABASE HELPERS ---
DB_FILE = "users.json"
GLOBAL_DB = "global_city_state.json"

def load_json(file):
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            with open(file, "r") as f: return json.load(f)
        except: return {"incidents": [], "players": {}}
    return {"incidents": [], "players": {}} if "global" in file else {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

def generate_account_code():
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# --- STYLING & BACKGROUND ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return None

bin_str = get_base64('background.png')
bg_style = f"""
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("data:image/png;base64,{bin_str if bin_str else ""}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    html, body, [class*="css"], label, p {{ color: white !important; font-family: 'Courier New', monospace; }}
    h1 {{ color: #ff00aa; text-align: center; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }}
    .login-box {{ padding: 30px; border: 2px solid #00ffff; border-radius: 20px; background: rgba(15,15,15,0.85); box-shadow: 0 0 30px #00ffff; margin: auto; }}
    .stats-card {{ padding: 20px; border-radius: 10px; text-align: center; border: 2px solid; background: rgba(0,0,0,0.6); backdrop-filter: blur(8px); }}
    .available {{ border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }}
    .active {{ border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }}
    .completed {{ border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }}
    div.stButton > button {{ background-color: black; color: #00ffff; border: 2px solid #ff00aa; border-radius: 10px; font-weight: bold; width: 100%; }}
</style>
"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_location" not in st.session_state: st.session_state.user_location = {"lat": 25.7617, "lng": -80.1918}
if "selected_location" not in st.session_state: st.session_state.selected_location = None
if "confirmation_pending" not in st.session_state: st.session_state.confirmation_pending = False

users_db = load_json(DB_FILE)

# --- GATEWAY ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    mode = st.radio("PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
    if mode == "LOGIN":
        u_in = st.text_input("OPERATOR ID")
        p_in = st.text_input("CIPHER", type="password")
        if st.button("INITIALIZE"):
            if u_in in users_db and users_db[u_in]["password"] == p_in:
                st.session_state.logged_in, st.session_state.current_user = True, u_in
                st.rerun()
    else:
        new_u = st.text_input("NAME")
        new_p = st.text_input("SET CIPHER", type="password")
        if st.button("REGISTER"):
            if new_u and new_p:
                users_db[new_u] = {
                    "password": new_p, "respect": 50, "xp": 0, "done": 0, "active": 0,
                    "active_list": [], "history": [], "join_date": str(date.today()),
                    "code": generate_account_code(), "truth_index": 50
                }
                save_json(DB_FILE, users_db)
                st.success("REGISTERED. LOGIN NOW.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN INTERFACE ---
else:
    user_data = users_db[st.session_state.current_user]
    global_data = load_json(GLOBAL_DB)
    page = st.sidebar.selectbox("📂 MENU", ["Missions", "Tactical Map", "Profile"])
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # --- PAGE: MISSIONS ---
    if page == "Missions":
        st.markdown("<h1>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stats-card available"><h3>12</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stats-card active"><h3>{user_data.get("active", 0)}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stats-card completed"><h3>{user_data.get("done", 0)}</h3><p>COMPLETED</p></div>', unsafe_allow_html=True)

        st.markdown("### 🎯 AVAILABLE MISSIONS")
        m_cols = st.columns(3)
        missions = [
            ("BEACH CLEANUP", "Clear debris from Ocean Beach.", 5),
            ("FOOD DRIVE", "Help distribute meals downtown.", 5),
            ("CODING WORKSHOP", "Mentor local teens in Python.", 10)
        ]
        for i, (title, desc, pts) in enumerate(missions):
            with m_cols[i]:
                with st.container(border=True):
                    st.subheader(title)
                    st.write(desc)
                    if st.button(f"ACCEPT {title}", key=f"m{i}"):
                        users_db[st.session_state.current_user]["active"] += 1
                        users_db[st.session_state.current_user]["xp"] += pts
                        users_db[st.session_state.current_user]["history"].append(f"Accepted {title}")
                        save_json(DB_FILE, users_db)
                        st.toast(f"Mission {title} Active!")

    # --- PAGE: TACTICAL MAP ---
    elif page == "Tactical Map":
        st.markdown("<h1>🚨 TACTICAL OVERLAY</h1>", unsafe_allow_html=True)
        col_left, col_right = st.columns([1.2, 2.5])
        
        with col_right:
            crimes_json = json.dumps(global_data.get("incidents", []))
            user_lat, user_lng = st.session_state.user_location['lat'], st.session_state.user_location['lng']
            
            map_html = f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
            <div id="map" style="width: 100%; height: 500px; background: #1a1a1a;"></div>
            <script>
                var map = L.map('map').setView([{user_lat}, {user_lng}], 13);
                L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}.png').addTo(map);
                L.circleMarker([{user_lat}, {user_lng}], {{radius: 12, fillColor: '#00ff00', color: '#fff', weight: 3, fillOpacity: 0.9}}).addTo(map);
                var crimes = {crimes_json};
                crimes.forEach(function(c) {{
                    L.circleMarker([c.lat, c.lng], {{radius: 10, fillColor: '#ff00aa', color: '#fff', fillOpacity: 0.8}}).bindPopup(c.type).addTo(map);
                }});
            </script>
            """
            components.html(map_html, height=520)

            # Movement Controls
            mc1, mc2, mc3 = st.columns(3)
            if mc2.button("⬆️ NORTH"): st.session_state.user_location['lat'] += 0.002; st.rerun()
            if mc1.button("⬅️ WEST"): st.session_state.user_location['lng'] -= 0.002; st.rerun()
            if mc3.button("➡️ EAST"): st.session_state.user_location['lng'] += 0.002; st.rerun()
            if st.button("🚨 REPORT AT CURRENT LOCATION"):
                st.session_state.confirmation_pending = True; st.rerun()

        with col_left:
            st.write("📋 **DISPATCH CONSOLE**")
            c_type = st.selectbox("Crime Type", ["Robbery", "GTA", "Drug Deal", "Vandalism"])
            if st.session_state.confirmation_pending:
                if st.button("✅ CONFIRM REPORT"):
                    new_crime = {"lat": st.session_state.user_location['lat'], "lng": st.session_state.user_location['lng'], "type": c_type}
                    global_data["incidents"].append(new_crime)
                    save_json(GLOBAL_DB, global_data)
                    st.session_state.confirmation_pending = False
                    st.success("Broadcasted!")
                    st.rerun()

    # --- PAGE: PROFILE ---
    elif page == "Profile":
        st.markdown("<h1>👤 OPERATOR PROFILE</h1>", unsafe_allow_html=True)
        level = user_data["xp"] // 100 + 1
        tier = "🥈 Silver" if user_data["respect"] < 70 else "💎 Diamond"
        
        st.markdown(f"""<div class="login-box">
            <h3>ID: {user_data['code']}</h3>
            <h3>Tier: {tier} | Level: {level}</h3>
            <h3>Respect: {user_data['respect']}% | XP: {user_data['xp']}</h3>
            <p>Joined: {user_data['join_date']}</p>
        </div>""", unsafe_allow_html=True)
        st.progress((user_data["xp"] % 100) / 100)
        
        st.divider()
        st.subheader("📜 Recent History")
        for h in reversed(user_data["history"][-5:]): st.write("✅", h)