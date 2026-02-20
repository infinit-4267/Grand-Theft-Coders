import streamlit as st
import random
import json
import os
import string
import base64
from PIL import Image, ImageDraw

# 1. Page Configuration
st.set_page_config(page_title="Vice City Intelligence", layout="wide")

# --- ROBUST DATABASE HELPERS ---
DB_FILE = "users.json"
GLOBAL_DB = "global_city_state.json"

def load_json(file):
    # Fix for JSONDecodeError: Check if file exists and isn't empty
    if os.path.exists(file) and os.path.getsize(file) > 0:
        try:
            with open(file, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {"incidents": [], "players": {}, "reports": []}
    
    # Default structures if file is missing or empty
    if file == DB_FILE: return {}
    return {"incidents": [], "players": {}, "reports": []}

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)

def generate_account_code():
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# --- ASSETS & CSS ---
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
    html, body, [class*="css"], label, p {{ color: #ff00aa !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #ff00aa; }}
    h1 {{ color: #ff00aa; text-align: center; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }}
    .stButton > button {{
        background-color: black !important; color: #00ffff !important;
        border: 2px solid #ff00aa !important; border-radius: 12px;
        font-weight: bold; box-shadow: 0 0 10px #ff00aa; width: 100%;
    }}
    .briefing-box {{ background: rgba(255, 0, 170, 0.12); border-left: 5px solid #ff00aa; padding: 15px; margin: 10px 0; }}
</style>
"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "pos_x" not in st.session_state: st.session_state.pos_x, st.session_state.pos_y = 827, 584 

users_db = load_json(DB_FILE)

# --- GATEWAY ---
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 GATEWAY</h1>", unsafe_allow_html=True)
    mode = st.radio("PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if mode == "LOGIN":
            u_in = st.text_input("OPERATOR ID")
            p_in = st.text_input("SECURITY CIPHER", type="password")
            if st.button("INITIALIZE"):
                if u_in in users_db and users_db[u_in]["password"] == p_in:
                    st.session_state.logged_in = True
                    st.session_state.current_user = u_in
                    st.rerun()
        else:
            new_u = st.text_input("NAME")
            new_p = st.text_input("CIPHER", type="password")
            if st.button("REGISTER"):
                if new_u and new_p:
                    users_db[new_u] = {"password": new_p, "respect": 50, "code": generate_account_code(), "active": 0, "done": 0, "truth_index": 50}
                    save_json(DB_FILE, users_db)
                    st.success("REGISTERED. LOGIN NOW.")

# --- MAIN INTERFACE ---
else:
    user_data = users_db[st.session_state.current_user]
    global_data = load_json(GLOBAL_DB)

    # Sidebar Navigation
    st.sidebar.markdown(f"## 👤 {st.session_state.current_user}")
    st.sidebar.markdown(f"**Respect:** {user_data['respect']}% | **Truth:** {user_data['truth_index']}%")
    
    st.sidebar.markdown("### 🕹️ NAVIGATION")
    step = 40
    c1, c2, c3 = st.sidebar.columns(3)
    if c2.button("▲"): st.session_state.pos_y -= step
    c4, c5, c6 = st.sidebar.columns(3)
    if c4.button("◀"): st.session_state.pos_x -= step
    if c6.button("▶"): st.session_state.pos_x += step
    c7, c8, c9 = st.sidebar.columns(3)
    if c8.button("▼"): st.session_state.pos_y += step

    # Update Global Player Position
    if "players" not in global_data: global_data["players"] = {}
    global_data["players"][st.session_state.current_user] = {"x": st.session_state.pos_x, "y": st.session_state.pos_y}
    save_json(GLOBAL_DB, global_data)

    # --- TABS FOR FEATURES ---
    tab1, tab2, tab3 = st.tabs(["🛰️ TACTICAL MAP", "🎯 MISSIONS", "🚨 REPORT INTEL"])

    with tab1:
        st.markdown("### LIVE OPERATOR TRACKING")
        def draw_map():
            try: img = Image.open("map.jpg").convert("RGBA")
            except: img = Image.new("RGBA", (1654, 1169), (20, 20, 20))
            draw = ImageDraw.Draw(img)
            for inc in global_data.get("incidents", []):
                draw.ellipse([inc['x']-15, inc['y']-15, inc['x']+15, inc['y']+15], fill=(255, 0, 170))
            draw.ellipse([st.session_state.pos_x-15, st.session_state.pos_y-15, st.session_state.pos_x+15, st.session_state.pos_y+15], fill="#00ffff", outline="white", width=3)
            return img
        st.image(draw_map(), use_column_width=True)
        
        # Proximity Logic
        for inc in global_data.get("incidents", []):
            dist = ((st.session_state.pos_x - inc['x'])**2 + (st.session_state.pos_y - inc['y'])**2)**0.5
            if dist < 120:
                st.error(f"🚨 NEARBY: {inc['type']}")
                if st.button(f"VERIFY {inc['id']}"):
                    st.success("VERIFIED. Truth Index +5")

    with tab2:
        st.markdown("### AVAILABLE MISSIONS")
        m1, m2 = st.columns(2)
        with m1:
            st.markdown("<div class='briefing-box'><b>BEACH CLEANUP</b><br>Clear Ocean Beach. Reward: +5 Respect</div>", unsafe_allow_html=True)
            if st.button("ACCEPT BEACH MISSION"): st.toast("Mission Active")
        with m2:
            st.markdown("<div class='briefing-box'><b>FOOD DRIVE</b><br>Serve Downtown. Reward: +5 Respect</div>", unsafe_allow_html=True)
            if st.button("ACCEPT FOOD MISSION"): st.toast("Mission Active")

    with tab3:
        st.markdown("### BROADCAST INTEL")
        i_type = st.selectbox("Type", ["Vandalism", "Theft", "Suspicious"])
        i_desc = st.text_area("Details")
        if st.button("SEND TO BUREAU"):
            new_inc = {"id": f"INC-{random.randint(100,999)}", "type": i_type, "x": st.session_state.pos_x, "y": st.session_state.pos_y}
            global_data["incidents"].append(new_inc)
            save_json(GLOBAL_DB, global_data)
            st.success("Incident Broadcasted at your current position!")

    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()