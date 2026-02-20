import streamlit as st
import random
import json
import os
import string
import base64
from PIL import Image, ImageDraw

# 1. Page Configuration
st.set_page_config(page_title="Vice City Intelligence", layout="wide")

# --- SHARED DATABASE HELPERS ---
DB_FILE = "users.json"
GLOBAL_DB = "global_city_state.json" # Shared across all users

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f: return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

# --- THE BACKGROUND FIX ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f: return base64.b64encode(f.read()).decode()

try:
    bin_str = get_base64('background.png')
    bg_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0, 0, 0, 0.6), rgba(0, 0, 0, 0.6)), url("data:image/png;base64,{bin_str}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    </style>"""
except:
    bg_style = """<style>.stApp { background-color: #0d0221; }</style>"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- NEON CSS ---
st.markdown("""
<style>
    html, body, [class*="css"] { color: #ff00aa !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #ff00aa; }
    h1 { color: #ff00aa; text-align: center; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }
    
    /* Neon D-Pad */
    .stButton > button {
        background-color: black !important; color: #00ffff !important;
        border: 2px solid #ff00aa !important; border-radius: 12px;
        font-weight: bold; box-shadow: 0 0 10px #ff00aa;
    }
    .stButton > button:hover { background-color: #ff00aa !important; color: white !important; }

    .stats-card { padding: 20px; border-radius: 10px; text-align: center; border: 2px solid; background: rgba(0,0,0,0.6); }
    .available { border-color: #00ffff; } .active { border-color: #ff00aa; } .completed { border-color: #00ffaa; }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
# Player spawns at center
if "pos_x" not in st.session_state: st.session_state.pos_x, st.session_state.pos_y = 827, 584 

users_db = load_json(DB_FILE)

# --- LOGIN GATE ---
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    user_input = st.text_input("OPERATOR ID")
    pw_input = st.text_input("SECURITY CIPHER", type="password")
    if st.button("INITIALIZE SESSION"):
        if user_input in users_db and users_db[user_input]["password"] == pw_input:
            st.session_state.logged_in = True
            st.session_state.current_user = user_input
            st.rerun()

# --- MAIN ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    global_data = load_json(GLOBAL_DB)

    # 1. SIDEBAR NAVIGATION (Joystick)
    st.sidebar.markdown("### 🕹️ NEON JOYSTICK")
    step = 30
    c1, c2, c3 = st.sidebar.columns(3)
    with c2: 
        if st.button("▲"): st.session_state.pos_y -= step
    c4, c5, c6 = st.sidebar.columns(3)
    with c4: 
        if st.button("◀"): st.session_state.pos_x -= step
    with c6: 
        if st.button("▶"): st.session_state.pos_x += step
    c7, c8, c9 = st.sidebar.columns(3)
    with c8: 
        if st.button("▼"): st.session_state.pos_y += step

    # Sync position to Global DB so others can see
    if "players" not in global_data: global_data["players"] = {}
    global_data["players"][st.session_state.current_user] = {"x": st.session_state.pos_x, "y": st.session_state.pos_y}
    save_json(GLOBAL_DB, global_data)

    # 2. TACTICAL MAP RENDERING
    def draw_map():
        try: img = Image.open("map.jpg").convert("RGBA")
        except: img = Image.new("RGBA", (1654, 1169), (20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # Draw Incidents
        for inc in global_data.get("incidents", []):
            draw.ellipse([inc['x']-15, inc['y']-15, inc['x']+15, inc['y']+15], fill=(255, 0, 170))
        
        # Draw Self as a glowing Cyan dot
        x, y = st.session_state.pos_x, st.session_state.pos_y
        draw.ellipse([x-20, y-20, x+20, y+20], outline="#00ffff", width=5)
        return img

    st.image(draw_map(), use_column_width=True)

    # 3. RADIUS THINKING SYSTEM
    st.divider()
    for inc in global_data.get("incidents", []):
        # Calculate distance to incidents
        dist = ((st.session_state.pos_x - inc['x'])**2 + (st.session_state.pos_y - inc['y'])**2)**0.5
        if dist < 100:
            st.error(f"🚨 PROXIMITY ALERT: {inc['type']} DETECTED")
            if st.button(f"VERIFY INTEL @ {inc['id']}"):
                st.success("INTEL VERIFIED: Misinformation Redirected. Social Index Increased.")
                # Logic to remove incident once verified