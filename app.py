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
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def generate_account_code():
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# --- THE BACKGROUND FIX ---
def get_base64(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return ""

bin_str = get_base64('background.png')
bg_style = f"""
<style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("data:image/png;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }}
    header[data-testid="stHeader"] {{
        background: rgba(0,0,0,0) !important;
    }}
</style>
"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- NEON CSS ---
st.markdown("""
<style>
    html, body, [class*="css"] { color: white; font-family: 'Courier New', Courier, monospace; }
    h1 { color: #ff00aa; text-align: center; font-size: 55px; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }
    h3 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
    .login-box { 
        padding: 40px; 
        border: 2px solid #00ffff; 
        border-radius: 20px; 
        background-color: rgba(15, 15, 15, 0.85); 
        backdrop-filter: blur(12px); 
        box-shadow: 0 0 30px #00ffff;
        max-width: 500px;
        margin: auto;
    }
    .stats-card {
        padding: 20px; border-radius: 10px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
    }
    .available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
    .active { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
    .completed { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }
    .badge { padding: 2px 8px; border-radius: 20px; font-size: 12px; border: 1px solid; }
    .easy { color: #00ffaa; border-color: #00ffaa; }
    .medium { color: #ffaa00; border-color: #ffaa00; }
    div.stButton > button {
        background-color: black; color: #00ffff; border: 2px solid #ff00aa;
        border-radius: 10px; font-weight: bold; width: 100%; height: 45px;
    }
    div.stButton > button:hover {
        background-color: #ff00aa; color: white; box-shadow: 0 0 20px #ff00aa;
    }
    .confirmation-box {
        padding: 20px;
        border: 2px solid #00ffff;
        border-radius: 10px;
        background-color: rgba(0, 20, 40, 0.9);
        box-shadow: 0 0 20px #00ffff;
        margin: 10px 0;
    }
    .user-location-box {
        padding: 15px;
        border: 2px solid #00ff00;
        border-radius: 10px;
        background-color: rgba(0, 40, 0, 0.9);
        box-shadow: 0 0 15px #00ff00;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "active_crimes" not in st.session_state:
    st.session_state.active_crimes = [
        {"name": "Downtown Miami", "lat": 25.7617, "lng": -80.1918, "type": "Drug Deal"},
        {"name": "Port of Miami", "lat": 25.7705, "lng": -80.1893, "type": "Robbery"}
    ]
if "user_location" not in st.session_state:
    st.session_state.user_location = {"lat": 25.7617, "lng": -80.1918}
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "confirmation_pending" not in st.session_state:
    st.session_state.confirmation_pending = False

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
            if new_u and new_p and new_u not in users_db:
                code = generate_account_code()
                users_db[new_u] = {
                    "password": new_p, "respect": 50, "xp": 0, "done": 0, "active": 0,
                    "history": [], "join_date": str(date.today()), "active_list": [],
                    "code": code
                }
                save_users(users_db)
                st.success(f"ID {code} ASSIGNED. SWITCH TO LOGIN.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    page = st.sidebar.selectbox("📂 NAVIGATION", ["Missions & Reports", "Operator Profile"])
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    if page == "Missions & Reports":
        # Dashboard Header
        st.markdown("<h1>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center;'>COMMUNITY MISSIONS · YOUR CHOICE · REAL IMPACT</p>", unsafe_allow_html=True)

        # Stats Row
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stats-card available"><h3>12</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stats-card active"><h3>{user_data.get("active", 0)}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stats-card completed"><h3>{user_data.get("done", 0)}</h3><p>COMPLETED</p></div>', unsafe_allow_html=True)

        # Mission Grid
        st.markdown("### 🎯 AVAILABLE MISSIONS")
        m1_col, m2_col, m3_col = st.columns(3)

        def create_mission(col, title, badge_text, badge_class, desc, key, points):
            with col:
                with st.container(border=True):
                    st.markdown(f"<span class='badge {badge_class}'>{badge_text}</span>", unsafe_allow_html=True)
                    st.subheader(title)
                    st.write(desc)
                    if st.button("ACCEPT MISSION", key=key):
                        users_db[st.session_state.current_user]["active"] += 1
                        users_db[st.session_state.current_user]["xp"] += points
                        users_db[st.session_state.current_user]["history"].append(f"Accepted {title} mission")
                        save_users(users_db)
                        st.rerun()

        create_mission(m1_col, "BEACH CLEANUP", "EASY", "easy", "Clear debris from Ocean Beach.", "m1_btn", 5)
        create_mission(m2_col, "FOOD DRIVE", "EASY", "easy", "Help distribute meals downtown.", "m2_btn", 5)
        create_mission(m3_col, "CODING WORKSHOP", "MEDIUM", "medium", "Mentor local teens in Python.", "m3_btn", 10)

        # --- INTERACTIVE MAP DISPLAY ---
        st.divider()
        st.markdown("### 🚨 LIVE CRIMINAL ACTIVITY TRACKER")
        col_left, col_right = st.columns([1.2, 2.5])
        
        with col_right:
            st.write("**📍 Use arrow buttons to move your location**")
            crimes_json = json.dumps(st.session_state.active_crimes)
            u_lat, u_lng = st.session_state.user_location['lat'], st.session_state.user_location['lng']
            
            map_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
                <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
                <style>#map {{ width: 100%; height: 520px; background: #1a1a1a; }} body {{margin:0;}}</style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([{u_lat}, {u_lng}], 11);
                    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}.png').addTo(map);
                    L.circleMarker([{u_lat}, {u_lng}], {{radius: 12, fillColor: '#00ff00', color: '#fff', weight: 3, fillOpacity: 0.9}}).bindPopup('<b>YOU</b>').addTo(map);
                    var crimes = {crimes_json};
                    crimes.forEach(function(c) {{
                        L.circleMarker([c.lat, c.lng], {{radius: 10, fillColor: '#ff00aa', color: '#fff', fillOpacity: 0.8}}).addTo(map);
                    }});
                </script>
            </body>
            </html>
            """
            components.html(map_html, height=530)

            # JOYSTICK
            st.write("**🎮 Move Your Location:**")
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

            st.markdown(f'<div class="user-location-box"><b>🟢 POSITION</b><br/>Lat: {u_lat:.4f} | Lng: {u_lng:.4f}</div>', unsafe_allow_html=True)

        with col_left:
            st.write("📋 **DISPATCH CONSOLE**")
            c_type = st.selectbox("Crime Type", ["Robbery", "GTA", "Drug Deal", "Vandalism", "Natural Disaster"])
            if st.button("🚨 REPORT AT CURRENT LOCATION"):
                st.session_state.selected_location = {"lat": u_lat, "lng": u_lng}
                st.session_state.confirmation_pending = True
                st.rerun()
            
            if st.session_state.confirmation_pending:
                st.markdown('<div class="confirmation-box">', unsafe_allow_html=True)
                st.write(f"Confirm {c_type} at current location?")
                if st.button("✅ CONFIRM BROADCAST"):
                    st.session_state.active_crimes.append({"name": "Reported Site", "lat": u_lat, "lng": u_lng, "type": c_type})
                    st.session_state.confirmation_pending = False
                    st.success("Intel Shared.")
                    st.rerun()
                if st.button("❌ CANCEL"): st.session_state.confirmation_pending = False; st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

            if st.button("🧹 CLEAR ALL REPORTS"):
                st.session_state.active_crimes = []
                st.rerun()

    elif page == "Operator Profile":
        st.markdown("<h1>👤 OPERATOR PROFILE</h1>", unsafe_allow_html=True)
        level = user_data["xp"] // 100 + 1
        xp_progress = (user_data["xp"] % 100) / 100
        tier = "🥈 Silver" if user_data["respect"] < 70 else "💎 Diamond"
        
        st.markdown(f"""
        <div class="login-box">
            <h3>ID: {user_data['code']}</h3>
            <h3>Rank: Street Associate</h3>
            <h3>Tier: {tier} | Level: {level}</h3>
            <h3>Respect: {user_data['respect']}% | XP: {user_data['xp']}</h3>
            <h3>Joined: {user_data['join_date']}</h3>
        </div>
        """, unsafe_allow_html=True)
        st.progress(xp_progress)
        
        st.divider()
        st.subheader("📜 Recent History")
        if user_data["history"]:
            for h in reversed(user_data["history"][-5:]): st.write("✅", h)
        else: st.info("No missions completed yet.")