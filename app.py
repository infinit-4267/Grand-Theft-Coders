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

def load_users():
    if os.path.exists(DB_FILE) and os.path.getsize(DB_FILE) > 0:
        try:
            with open(DB_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def generate_account_code():
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# --- THE BACKGROUND FIX ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()
    except: return ""

bin_str = get_base64('background.png')
st.markdown(f"""
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("data:image/png;base64,{bin_str}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    html, body, [class*="css"], label, p {{ color: white !important; font-family: 'Courier New', monospace; }}
    h1 {{ color: #ff00aa; text-align: center; font-size: 55px; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }}
    .login-box {{ padding: 30px; border: 2px solid #00ffff; border-radius: 20px; background: rgba(15,15,15,0.85); box-shadow: 0 0 30px #00ffff; margin: auto; }}
    .stats-card {{ padding: 20px; border-radius: 10px; text-align: center; border: 2px solid; background: rgba(0,0,0,0.6); }}
    .confirmation-box {{ padding: 20px; border: 2px solid #00ffff; border-radius: 10px; background: rgba(0, 20, 40, 0.9); box-shadow: 0 0 20px #00ffff; }}
    div.stButton > button {{ background-color: black; color: #00ffff; border: 2px solid #ff00aa; border-radius: 10px; font-weight: bold; width: 100%; height: 45px; }}
    div.stButton > button:hover {{ background-color: #ff00aa; color: white; box-shadow: 0 0 20px #ff00aa; }}
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "active_crimes" not in st.session_state:
    st.session_state.active_crimes = [
        {"name": "Downtown Miami", "lat": 25.7617, "lng": -80.1918, "type": "Drug Deal"},
        {"name": "Port of Miami", "lat": 25.7705, "lng": -80.1893, "type": "Robbery"}
    ]
if "user_location" not in st.session_state: st.session_state.user_location = {"lat": 25.7617, "lng": -80.1918}
if "confirmation_pending" not in st.session_state: st.session_state.confirmation_pending = False
if "selected_location" not in st.session_state: st.session_state.selected_location = None

users_db = load_users()

# --- GATEWAY ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    mode = st.radio("SELECT PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
    if mode == "LOGIN":
        u_in = st.text_input("OPERATOR ID")
        p_in = st.text_input("SECURITY CIPHER", type="password")
        if st.button("INITIALIZE SESSION"):
            if u_in in users_db and users_db[u_in]["password"] == p_in:
                st.session_state.logged_in, st.session_state.current_user = True, u_in
                st.rerun()
            else: st.error("ACCESS DENIED")
    else:
        new_u = st.text_input("CHOOSE OPERATOR NAME")
        new_p = st.text_input("SET CIPHER", type="password")
        if st.button("GENERATE ID & REGISTER"):
            if new_u and new_p:
                users_db[new_u] = {"password": new_p, "respect": 50, "xp": 0, "done": 0, "active": 0, "history": [], "join_date": str(date.today()), "active_list": [], "code": generate_account_code()}
                save_users(users_db)
                st.success("REGISTERED. PLEASE LOGIN.")
    st.markdown('</div>', unsafe_allow_html=True)

else:
    user_data = users_db[st.session_state.current_user]
    page = st.sidebar.selectbox("📂 NAVIGATION", ["Missions & Tactical Map", "Operator Profile"])
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    if page == "Missions & Tactical Map":
        st.markdown("<h1>🎯 MISSIONS & INTEL</h1>", unsafe_allow_html=True)
        # Stats Row
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stats-card available"><h3>12</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stats-card active"><h3>{user_data.get("active", 0)}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stats-card completed"><h3>{user_data.get("done", 0)}</h3><p>COMPLETED</p></div>', unsafe_allow_html=True)

        # Mission Grid
        st.markdown("### 🎯 DISPATCH MISSIONS")
        m_cols = st.columns(3)
        missions = [("BEACH CLEANUP", "Ocean Beach", 5), ("FOOD DRIVE", "Downtown", 5), ("PYTHON WORKSHOP", "Tech Hub", 10)]
        for i, (title, desc, pts) in enumerate(missions):
            with m_cols[i]:
                with st.container(border=True):
                    st.subheader(title)
                    st.write(desc)
                    if st.button(f"ACCEPT {title}", key=f"m_{i}"):
                        users_db[st.session_state.current_user]["xp"] += pts
                        users_db[st.session_state.current_user]["done"] += 1
                        users_db[st.session_state.current_user]["history"].append(f"Completed {title}")
                        save_users(users_db)
                        st.toast("XP Earned!")

        st.divider()
        st.markdown("### 🚨 LIVE CRIMINAL ACTIVITY TRACKER")
        col_left, col_right = st.columns([1.2, 2.5])
        
        with col_right:
            st.write("**📍 Tactical Map Controls**")
            crimes_json = json.dumps(st.session_state.active_crimes)
            u_lat, u_lng = st.session_state.user_location['lat'], st.session_state.user_location['lng']
            
            map_html = f"""
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
            <div id="map" style="width: 100%; height: 500px; background: #1a1a1a;"></div>
            <script>
                var map = L.map('map').setView([{u_lat}, {u_lng}], 11);
                L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}.png').addTo(map);
                L.circleMarker([{u_lat}, {u_lng}], {{radius: 12, fillColor: '#00ff00', color: '#fff', weight: 3, fillOpacity: 0.9}}).addTo(map);
                var crimes = {crimes_json};
                var colors = {{ 'Robbery': '#ff0000', 'GTA': '#ff9900', 'Drug Deal': '#8000ff', 'Vandalism': '#ffff00', 'Natural Disaster': '#0064ff' }};
                crimes.forEach(function(c) {{
                    L.circleMarker([c.lat, c.lng], {{radius: 10, fillColor: colors[c.type] || '#ff0000', color: '#fff', fillOpacity: 0.8}}).addTo(map);
                }});
            </script>
            """
            components.html(map_html, height=520)

            # Map Legend Restored
            st.write("**Map Legend:**")
            l_cols = st.columns(5)
            l_cols[0].markdown("🟢 Your Location")
            l_cols[1].markdown("🔴 Robbery")
            l_cols[2].markdown("🟠 GTA")
            l_cols[3].markdown("🟣 Drug Deal")
            l_cols[4].markdown("🟡 Vandalism")

            # JOYSTICK WITH SOUTH RESTORED
            j1, j2, j3 = st.columns(3)
            with j2: 
                if st.button("⬆️ NORTH"): st.session_state.user_location['lat'] += 0.002; st.rerun()
            j4, j5, j6 = st.columns(3)
            with j4: 
                if st.button("⬅️ WEST"): st.session_state.user_location['lng'] -= 0.002; st.rerun()
            with j6: 
                if st.button("➡️ EAST"): st.session_state.user_location['lng'] += 0.002; st.rerun()
            j7, j8, j9 = st.columns(3)
            with j8: 
                if st.button("⬇️ SOUTH"): st.session_state.user_location['lat'] -= 0.002; st.rerun()

        with col_left:
            st.write("📋 **DISPATCH CONSOLE**")
            c_type = st.selectbox("INTEL TYPE", ["Robbery", "GTA", "Drug Deal", "Vandalism", "Natural Disaster"])
            if st.button("🚨 REPORT AT CURRENT POSITION"):
                st.session_state.selected_location = {"lat": u_lat, "lng": u_lng}
                st.session_state.confirmation_pending = True; st.rerun()
            
            if st.session_state.confirmation_pending:
                st.markdown('<div class="confirmation-box">', unsafe_allow_html=True)
                st.write(f"Broadcast {c_type}?")
                if st.button("✅ CONFIRM"):
                    st.session_state.active_crimes.append({"lat": u_lat, "lng": u_lng, "type": c_type})
                    st.session_state.confirmation_pending = False; st.rerun()
                if st.button("❌ CANCEL"): st.session_state.confirmation_pending = False; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            if st.button("🧹 CLEAR ALL REPORTS"):
                st.session_state.active_crimes = []; st.rerun()

    elif page == "Operator Profile":
        st.markdown("<h1>👤 OPERATOR PROFILE</h1>", unsafe_allow_html=True)
        level = user_data["xp"] // 100 + 1
        st.markdown(f'<div class="login-box"><h3>ID: {user_data["code"]}</h3><h3>Rank: Associate | Level: {level}</h3><h3>Respect: {user_data["respect"]}% | XP: {user_data["xp"]}</h3></div>', unsafe_allow_html=True)
        st.progress((user_data["xp"] % 100) / 100)
        st.subheader("📜 RECENT MISSIONS")
        for h in reversed(user_data["history"][-5:]): st.write("✅", h)