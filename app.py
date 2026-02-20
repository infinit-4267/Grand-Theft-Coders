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
    with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()

try:
    bin_str = get_base64('background.png')
    bg_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url("data:image/png;base64,{bin_str}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    html, body, [class*="css"] {{ color: white; font-family: 'Courier New', monospace; }}
    h1 {{ color: #ff00aa; text-align: center; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }}
    .login-box {{ padding: 30px; border: 2px solid #00ffff; border-radius: 20px; background: rgba(15,15,15,0.85); box-shadow: 0 0 30px #00ffff; margin: auto; }}
    </style>"""
    st.markdown(bg_style, unsafe_allow_html=True)
except:
    st.markdown("<style>.stApp { background-color: #0d0221; }</style>", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_location" not in st.session_state: st.session_state.user_location = {"lat": 25.7617, "lng": -80.1918}

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
        new_u = st.text_input("OPERATOR NAME")
        new_p = st.text_input("SET CIPHER", type="password")
        if st.button("REGISTER"):
            if new_u and new_p and new_u not in users_db:
                users_db[new_u] = {
                    "password": new_p, "respect": 50, "xp": 0, "done": 0, 
                    "active_list": [], "history": [], "join_date": str(date.today()),
                    "code": generate_account_code()
                }
                save_json(DB_FILE, users_db)
                st.success("REGISTERED. SWITCH TO LOGIN.")
    st.markdown('</div>', unsafe_allow_html=True)

# --- MAIN ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    page = st.sidebar.selectbox("📂 MENU", ["Tactical Map", "Missions", "Profile"])
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # --- TAB 1: TACTICAL MAP & JOYSTICK ---
    if page == "Tactical Map":
        st.markdown("<h1>🚨 TACTICAL OVERLAY</h1>", unsafe_allow_html=True)
        # (Insert your friend's Leaflet map code here, using st.session_state.user_location)
        # Use st.columns for the North/South/East/West buttons to move the user
        st.info(f"Current GPS: {st.session_state.user_location['lat']:.4f}, {st.session_state.user_location['lng']:.4f}")

    # --- TAB 2: MISSIONS ---
    elif page == "Missions":
        st.markdown("<h1>🎯 ACTIVE MISSIONS</h1>", unsafe_allow_html=True)
        # Logic for accepting missions and adding XP

    # --- TAB 3: PROFILE (Integrated Friend's Code) ---
    elif page == "Profile":
        st.markdown("<h1>👤 OPERATOR PROFILE</h1>", unsafe_allow_html=True)
        
        # Calculate Level & Rank
        level = user_data["xp"] // 100 + 1
        xp_progress = (user_data["xp"] % 100) / 100
        rank = "Kingpin" if level > 10 else "Street Associate"
        
        # Respect Tiers
        if user_data["respect"] < 40: tier = "🥉 Bronze"
        elif user_data["respect"] < 70: tier = "🥈 Silver"
        elif user_data["respect"] < 90: tier = "🥇 Gold"
        else: tier = "💎 Diamond"

        st.markdown(f"""
        <div class="login-box">
            <h3>ID: {user_data['code']}</h3>
            <h3>Rank: {rank}</h3>
            <h3>Tier: {tier}</h3>
            <h3>Level: {level}</h3>
            <h3>Respect: {user_data['respect']}%</h3>
            <h3>Total XP: {user_data['xp']}</h3>
            <h3>Joined: {user_data['join_date']}</h3>
        </div>
        """, unsafe_allow_html=True)
        st.progress(xp_progress)
        
        st.divider()
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Completed", user_data["done"])
        col2.metric("Active", len(user_data["active_list"]))
        col3.metric("Respect %", user_data["respect"])
        col4.metric("Level", level)