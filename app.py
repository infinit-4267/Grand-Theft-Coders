import streamlit as st
import random
import json
import os
import string
import base64
from PIL import Image, ImageDraw

# 1. Page Configuration
st.set_page_config(page_title="Vice City Intelligence", layout="wide")

# --- DATABASE HELPERS ---
DB_FILE = "users.json"
GLOBAL_DB = "global_city_state.json"

def load_json(file):
    if os.path.exists(file):
        with open(file, "r") as f: return json.load(f)
    return {}

def save_json(file, data):
    with open(file, "w") as f: json.dump(data, f, indent=4)

def generate_account_code():
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# --- BACKGROUND ASSETS ---
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
    </style>"""
except:
    bg_style = """<style>.stApp { background-color: #0d0221; }</style>"""
st.markdown(bg_style, unsafe_allow_html=True)

# --- NEON CSS ---
st.markdown("""
<style>
    html, body, [class*="css"], label, p { color: #ff00aa !important; font-family: 'Courier New', monospace; text-shadow: 0 0 5px #ff00aa; }
    h1 { color: #ff00aa; text-align: center; font-size: 50px; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }
    
    .login-box { 
        padding: 30px; border: 2px solid #00ffff; border-radius: 20px; 
        background-color: rgba(15, 15, 15, 0.85); backdrop-filter: blur(10px); 
        box-shadow: 0 0 30px #00ffff; max-width: 500px; margin: auto;
    }

    .stButton > button {
        background-color: black !important; color: #00ffff !important;
        border: 2px solid #ff00aa !important; border-radius: 12px;
        font-weight: bold; box-shadow: 0 0 10px #ff00aa; width: 100%;
    }
    .stButton > button:hover { background-color: #ff00aa !important; color: white !important; box-shadow: 0 0 20px #ff00aa; }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "pos_x" not in st.session_state: st.session_state.pos_x, st.session_state.pos_y = 827, 584 

users_db = load_json(DB_FILE)

# --- SCREEN 1: THE GATEWAY (Login & Signup) ---
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h1>🌴 GATEWAY</h1>", unsafe_allow_html=True)
    
    mode = st.radio("SELECT PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
    
    if mode == "LOGIN":
        u_in = st.text_input("OPERATOR ID")
        p_in = st.text_input("SECURITY CIPHER", type="password")
        if st.button("INITIALIZE SESSION"):
            if u_in in users_db and users_db[u_in]["password"] == p_in:
                st.session_state.logged_in = True
                st.session_state.current_user = u_in
                st.rerun()
            else: st.error("ACCESS DENIED: Credentials Invalid")
            
    else:
        new_u = st.text_input("NEW OPERATOR NAME")
        new_p = st.text_input("SET CIPHER", type="password")
        if st.button("REGISTER OPERATOR"):
            if new_u and new_p and new_u not in users_db:
                code = generate_account_code()
                users_db[new_u] = {"password": new_p, "respect": 50, "code": code, "active": 0, "done": 0, "truth_index": 50}
                save_json(DB_FILE, users_db)
                st.success(f"ID {code} ASSIGNED. SWITCH TO LOGIN.")
            elif new_u in users_db: st.warning("Operator already exists.")
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- SCREEN 2: THE MAIN REPUTATION ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    global_data = load_json(GLOBAL_DB)

    # 1. SIDEBAR NAVIGATION & PROFILE
    st.sidebar.markdown(f"## 👤 {st.session_state.current_user}")
    with st.sidebar.expander("📂 OPERATOR PROFILE"):
        st.markdown(f"**ID:** `{user_data['code']}`")
        st.markdown(f"**TRUTH INDEX:** {user_data.get('truth_index', 50)}%")
    
    st.sidebar.markdown("### 🕹️ NAVIGATION")
    step = 40
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

    # Update Global Player State
    if "players" not in global_data: global_data["players"] = {}
    global_data["players"][st.session_state.current_user] = {"x": st.session_state.pos_x, "y": st.session_state.pos_y}
    save_json(GLOBAL_DB, global_data)

    # 2. TACTICAL MAP
    def draw_map():
        try: img = Image.open("map.jpg").convert("RGBA")
        except: img = Image.new("RGBA", (1654, 1169), (20, 20, 20))
        draw = ImageDraw.Draw(img)
        
        # Draw shared incidents
        for inc in global_data.get("incidents", []):
            draw.ellipse([inc['x']-15, inc['y']-15, inc['x']+15, inc['y']+15], fill=(255, 0, 170))
        
        # Draw self position
        x, y = st.session_state.pos_x, st.session_state.pos_y
        draw.ellipse([x-15, y-15, x+15, y+15], fill="#00ffff", outline="white", width=3)
        return img

    st.image(draw_map(), use_column_width=True)

    # 3. PROXIMITY VERIFICATION
    st.divider()
    for inc in global_data.get("incidents", []):
        dist = ((st.session_state.pos_x - inc['x'])**2 + (st.session_state.pos_y - inc['y'])**2)**0.5
        if dist < 120:
            st.error(f"🚨 NEARBY INTEL: {inc['type']}")
            if st.button(f"VERIFY @ {inc['id']}"):
                st.success("STATION SECURED: Misinformation Redirected.")
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()