import streamlit as st
import random
import json
import os
import string

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