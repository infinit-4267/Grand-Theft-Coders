import streamlit as st
import random
import json
import os
import string
import base64
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

# --- THE BACKGROUND FIX ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
    # Ensure 'background.png' is in your project folder
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
except:
    # Fallback if background.png is missing
    bg_style = """<style>.stApp { background-color: #0d0221; }</style>"""

st.markdown(bg_style, unsafe_allow_html=True)

# --- NEON CSS ---
st.markdown("""
<style>
    /* Global Text and Neon Titles */
    html, body, [class*="css"] { color: white; font-family: 'Courier New', Courier, monospace; }
    h1 { color: #ff00aa; text-align: center; font-size: 55px; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }
    h3 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }

    /* Login Box Container */
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

    /* Stats Cards */
    .stats-card {
        padding: 20px; border-radius: 10px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
    }
    .available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
    .active { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
    .completed { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }

    /* Mission Badges */
    .badge { padding: 2px 8px; border-radius: 20px; font-size: 12px; border: 1px solid; }
    .easy { color: #00ffaa; border-color: #00ffaa; }
    .medium { color: #ffaa00; border-color: #ffaa00; }
    
    /* Neon Buttons */
    div.stButton > button {
        background-color: black; color: #00ffff; border: 2px solid #ff00aa;
        border-radius: 10px; font-weight: bold; width: 100%; height: 45px;
    }
    div.stButton > button:hover {
        background-color: #ff00aa; color: white; box-shadow: 0 0 20px #ff00aa;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "active_crimes" not in st.session_state:
    st.session_state.active_crimes = [
        {"name": "Downtown", "x": 0.425, "y": 0.680, "type": "Drug Deal"},
        {"name": "Port of Miami", "x": 0.810, "y": 0.730, "type": "Smuggling"}
    ]

users_db = load_users()

# --- SCREEN 1: THE LOGIN/SIGNUP GATE ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    
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
                st.error("ACCESS DENIED: Cipher Mismatch")
    else:
        new_user = st.text_input("CHOOSE OPERATOR NAME")
        new_pw = st.text_input("SET CIPHER", type="password")
        if st.button("GENERATE ID & REGISTER"):
            if new_user and new_pw and new_user not in users_db:
                code = generate_account_code()
                users_db[new_user] = {"password": new_pw, "respect": 50, "code": code, "active": 0, "done": 0}
                save_users(users_db)
                st.success(f"ID {code} ASSIGNED. SWITCH TO LOGIN.")
            elif new_user in users_db:
                st.warning("Operator already exists.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- SCREEN 2: THE MAIN REPUTATION ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    
    # Sidebar Profile
    st.sidebar.markdown(f"## 👤 {st.session_state.current_user}")
    with st.sidebar.expander("📂 VIEW OPERATOR PROFILE"):
        st.markdown(f"**ID:** `{user_data['code']}`")
        st.markdown(f"**RANK:** Street Associate")
        st.markdown(f"**RESPECT:** {user_data['respect']}%")
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

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
    m1, m2, m3 = st.columns(3)

    # Define Mission Helper
    def create_mission(col, title, badge_text, badge_class, desc, key, points):
        with col:
            with st.container(border=True):
                st.markdown(f"<span class='badge {badge_class}'>{badge_text}</span>", unsafe_allow_html=True)
                st.subheader(title)
                st.write(desc)
                if st.button("ACCEPT MISSION", key=key):
                    users_db[st.session_state.current_user]["active"] += 1
                    users_db[st.session_state.current_user]["respect"] = min(user_data["respect"] + points, 100)
                    save_users(users_db)
                    st.rerun()

    create_mission(m1, "BEACH CLEANUP", "EASY", "easy", "Clear debris from Ocean Beach.", "m1_btn", 5)
    create_mission(m2, "FOOD DRIVE", "EASY", "easy", "Help distribute meals downtown.", "m2_btn", 5)
    create_mission(m3, "CODING WORKSHOP", "MEDIUM", "medium", "Mentor local teens in Python.", "m3_btn", 10)

    # --- TACTICAL MAP DISPLAY ---
    st.divider()
    st.markdown("### 🚨 LIVE CRIMINAL ACTIVITY TRACKER")
    
    def draw_intel_map():
        try:
            base_map = Image.open("map.jpg").convert("RGBA")
        except:
            base_map = Image.new("RGBA", (1654, 1169), (20, 20, 20))
        
        draw = ImageDraw.Draw(base_map)
        w, h = base_map.size
        
        for crime in st.session_state.active_crimes:
            px, py = crime['x'] * w, crime['y'] * h
            pin_color = (255, 0, 170, 255) 
            r = 15
            draw.ellipse([px-r, py-r*3, px+r, py-r], fill=pin_color, outline="white", width=2)
            draw.polygon([(px-r, py-r*2), (px+r, py-r*2), (px, py)], fill=pin_color, outline="white")
            draw.text((px + 20, py - 30), f"{crime['name'].upper()}\n{crime['type'].upper()}", fill="white")
        return base_map

    col_input, col_map_render = st.columns([1, 2.5])
    
    with col_input:
        st.write("Dispatch Console")
        c_name = st.text_input("Incident Location")
        c_type = st.selectbox("Crime Type", ["Robbery", "Grand Theft Auto", "Drug Deal", "Vandalism"])
        c_x = st.slider("Map X", 0.0, 1.0, 0.5)
        c_y = st.slider("Map Y", 0.0, 1.0, 0.5)
        
        if st.button("🚨 BROADCAST REPORT"):
            if c_name:
                st.session_state.active_crimes.append({"name": c_name, "x": c_x, "y": c_y, "type": c_type})
                st.rerun()
        if st.button("🧹 CLEAR MAP"):
            st.session_state.active_crimes = []
            st.rerun()

    with col_map_render:
        st.image(draw_intel_map(), use_column_width=True)