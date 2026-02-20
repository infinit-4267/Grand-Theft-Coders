import streamlit as st
import random
import json
import os
import string
from PIL import Image, ImageDraw

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

# --- CSS STYLING (The Neon Look) ---
st.markdown("""
<style>
    .stApp { background-color: #0d0221; color: white; }
    h1 { color: #ff00aa; text-align: center; text-shadow: 0 0 10px #ff00aa, 0 0 20px #00ffff; }
    
    /* Stats Cards */
    .stats-card {
        padding: 20px; border-radius: 10px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.3);
    }
    .available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
    .active { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
    .completed { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }
    /* Mission Cards */
    .badge { padding: 2px 8px; border-radius: 20px; font-size: 12px; border: 1px solid; }
    .easy { color: #00ffaa; border-color: #00ffaa; }
    .medium { color: #ffaa00; border-color: #ffaa00; }
    
    /* Buttons */
    div.stButton > button {
        background-color: black; color: #00ffff; border: 2px solid #ff00aa;
        border-radius: 10px; font-weight: bold; width: 100%;
    }
</style>
""", unsafe_allow_html=True)
# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# [NEW] Initialize the crime list if it doesn't exist
if "active_crimes" not in st.session_state:
    st.session_state.active_crimes = [
        {"name": "Downtown", "x": 0.425, "y": 0.680, "type": "Drug Deal"},
        {"name": "Port of Miami", "x": 0.810, "y": 0.730, "type": "Smuggling"}
    ]

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users_db = load_users()

# --- SCREEN 1: THE LOGIN/SIGNUP GATE ---
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        mode = st.radio("SELECT PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
        if mode == "LOGIN":
            user_input = st.text_input("OPERATOR ID")
            pw_input = st.text_input("SECURITY CIPHER", type="password")
            if st.button("INITIALIZE SESSION"):
                if user_input in users_db and users_db[user_input]["password"] == pw_input:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_input
                    st.rerun()
                else:
                    st.error("ACCESS DENIED")
        else:
            new_user = st.text_input("CHOOSE OPERATOR NAME")
            new_pw = st.text_input("SET CIPHER", type="password")
            if st.button("GENERATE ID & REGISTER"):
                if new_user and new_pw and new_user not in users_db:
                    code = generate_account_code()
                    users_db[new_user] = {"password": new_pw, "respect": 50, "code": code, "active": 0, "done": 0}
                    save_users(users_db)
                    st.success(f"ID GENERATED: {code}")
# --- SCREEN 2: THE MAIN REPUTATION ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    
    # Sidebar Profile
    st.sidebar.markdown(f"## 👤 {st.session_state.current_user}")
    with st.sidebar.expander("📂 VIEW OPERATOR PROFILE"):
        st.markdown(f"**ID:** `{user_data['code']}`")
        st.markdown(f"**RANK:** Street Associate")
        st.markdown(f"**RESPECT:** {user_data['respect']}")
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # Dashboard Header
    st.markdown("<h1>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>COMMUNITY MISSIONS · YOUR CHOICE · REAL IMPACT</p>", unsafe_allow_html=True)
    st.info("⚠️ ALL MISSIONS ARE VOLUNTARY · YOUR CHOICE MATTERS")
    # --- [NEW] CRIME TRACKER LOGIC ---
    districts = {
        "Downtown / Bayfront": {"x": 0.425, "y": 0.680, "crime": "Active: Drug Deal"},
        "Bayside Marketplace": {"x": 0.385, "y": 0.585, "crime": "Active: Shoplifting"},
        "Port of Miami": {"x": 0.810, "y": 0.730, "crime": "Active: Smuggling"},
        "Watson Island": {"x": 0.740, "y": 0.350, "crime": "Active: Street Race"},
        "Overtown": {"x": 0.150, "y": 0.220, "crime": "Active: Grand Theft Auto"},
    }

    def draw_intel_map():
        try:
            base_map = Image.open("map.jpg").convert("RGBA")
        except:
            base_map = Image.new("RGBA", (1654, 1169), (20, 20, 20))
        
        draw = ImageDraw.Draw(base_map)
        w, h = base_map.size
        
        # Loop through the functional session state list
        for crime in st.session_state.active_crimes:
            px, py = crime['x'] * w, crime['y'] * h
            pin_color = (255, 0, 170, 255) 
            
            # Draw Pin
            r = 15
            draw.ellipse([px-r, py-r*3, px+r, py-r], fill=pin_color, outline="white", width=2)
            draw.polygon([(px-r, py-r*2), (px+r, py-r*2), (px, py)], fill=pin_color, outline="white")
            draw.ellipse([px-5, py-r*2-5, px+5, py-r*2+5], fill="white")

            # Label
            draw.text((px + 20, py - 30), f"{crime['name'].upper()}\nREPORT: {crime['type'].upper()}", fill="white")
        return base_map
    # Stats Row
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stats-card available"><h3>12</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stats-card active"><h3>{user_data.get("active", 0)}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stats-card completed"><h3>{user_data.get("done", 0)}</h3><p>COMPLETED</p></div>', unsafe_allow_html=True)

    # Categories
    st.markdown("### ⭐ MISSION CATEGORIES")
    cat_cols = st.columns(6)
    cats = ["ALL MISSIONS", "COMMUNITY", "ENVIRONMENT", "EDUCATION", "SAFETY", "HEALTH"]
    for i, cat in enumerate(cats):
        cat_cols[i].button(cat, key=f"cat_{i}")

    # Mission Cards
    st.markdown("### 🎯 AVAILABLE MISSIONS")
    m1, m2, m3 = st.columns(3)

    with m1:
        with st.container(border=True):
            st.markdown("<span class='badge easy'>EASY</span> <small>ENVIRONMENT</small>", unsafe_allow_html=True)
            st.subheader("BEACH CLEANUP")
            st.write("Clean up the beachfront to protect marine life.")
            if st.button("ACCEPT MISSION", key="m1_btn"):
                users_db[st.session_state.current_user]["active"] += 1
                users_db[st.session_state.current_user]["respect"] = min(user_data["respect"] + 5, 100)
                save_users(users_db)
                st.rerun()

    with m2:
        with st.container(border=True):
            st.markdown("<span class='badge easy'>EASY</span> <small>COMMUNITY</small>", unsafe_allow_html=True)
            st.subheader("FOOD DRIVE")
            st.write("Distribute meals to members downtown.")
            if st.button("ACCEPT MISSION", key="m2_btn"):
                users_db[st.session_state.current_user]["active"] += 1
                users_db[st.session_state.current_user]["respect"] = min(user_data["respect"] + 5, 100)
                save_users(users_db)
                st.rerun()

    with m3:
        with st.container(border=True):
            st.markdown("<span class='badge medium'>MEDIUM</span> <small>EDUCATION</small>", unsafe_allow_html=True)
            st.subheader("CODING WORKSHOP")
            st.write("Teach basic programming to local teenagers.")
            if st.button("ACCEPT MISSION", key="m3_btn"):
                users_db[st.session_state.current_user]["active"] += 1
                users_db[st.session_state.current_user]["respect"] = min(user_data["respect"] + 10, 100)
                save_users(users_db)
                st.rerun()
    # --- [NEW] TACTICAL MAP DISPLAY ---
    st.divider()
    st.markdown("### 🚨 LIVE CRIMINAL ACTIVITY TRACKER")
    
    col_map_info, col_map_render = st.columns([1, 3])
    
    with col_map_info:
        st.write("Vercetti Bureau Satellite Feed")
        st.markdown("🔴 **Red Pins:** Active Crimes")
        if st.button("RESCAN CITY SENSORS"):
            st.rerun()

    with col_map_render:
        with st.spinner("Acquiring Satellite Lock..."):
            crime_map = draw_intel_map()
            st.image(crime_map, use_column_width=True, caption="VICE CITY CRIME FEED v1.0")
    # --- [NEW] FUNCTIONAL REPORTING SYSTEM ---
    st.divider()
    st.markdown("### 📡 CRIME DISPATCH CONSOLE")
    
    col_input, col_map_render = st.columns([1, 3])
    
    with col_input:
        st.write("Add Live Incident")
        c_name = st.text_input("Location Name", placeholder="e.g. Malibu Club")
        c_type = st.selectbox("Crime Type", ["Grand Theft Auto", "Drug Deal", "Robbery", "Vandalism"])
        
        # Coordinates - For the demo, you can use sliders or manual input
        # Pro-tip: 0.5 is center
        c_x = st.slider("X Coordinate", 0.0, 1.0, 0.5)
        c_y = st.slider("Y Coordinate", 0.0, 1.0, 0.5)
        
        if st.button("🚨 BROADCAST REPORT"):
            if c_name:
                new_incident = {"name": c_name, "x": c_x, "y": c_y, "type": c_type}
                st.session_state.active_crimes.append(new_incident)
                st.toast(f"Dispatching units to {c_name}!")
                st.rerun()
            else:
                st.error("Location name required!")

        if st.button("🧹 CLEAR ALL REPORTS"):
            st.session_state.active_crimes = []
            st.rerun()

    with col_map_render:
        crime_map = draw_intel_map()
        st.image(crime_map, use_column_width=True)