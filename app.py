import streamlit as st
import json
import os
import random
import string

# --- DB FUNCTIONS ---
DB_FILE = "users.json"

def load_data():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- INITIALIZE SESSION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- UI CUSTOMIZATION ---
st.markdown("""
<style>
    .stApp { background-color: #0d0221; color: white; }
    .stats-card {
        padding: 20px; border-radius: 10px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.3);
    }
    .available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
    .active { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
    .profile-sidebar {
        border: 1px solid #ff00aa; padding: 15px; border-radius: 10px;
        background: rgba(255, 0, 170, 0.1); text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    # (Insert your login/signup logic here from previous steps)
    st.title("🌴 VICE CITY LOGIN")
    user_db = load_data()
    user_name = st.text_input("Operator ID")
    if st.button("ENTER CITY"):
        if user_name in user_db:
            st.session_state.logged_in = True
            st.session_state.current_user = user_name
            st.rerun()

# --- MAIN DASHBOARD ---
else:
    user_db = load_data()
    user_name = st.session_state.current_user
    user_data = user_db[user_name]
    
    # Update mission counts for display
    active_m = user_data.get("active_missions", 0)
    completed_m = user_data.get("completed_missions", 0)

    # 1. SIDEBAR PROFILE
    with st.sidebar:
        st.markdown(f"""
        <div class="profile-sidebar">
            <h2 style="color:#ff00aa; margin:0;">{user_name.upper()}</h2>
            <p style="color:#00ffff; font-size:12px;">CODE: {user_data.get('code', 'N/A')}</p>
            <hr>
            <p><b>RESPECT:</b> {user_data.get('respect', 50)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # 2. HEADER
    st.markdown("<h1 style='text-align:center;'>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)
    
    # 3. STATS ROW
    c1, c2, c3 = st.columns(3)
    c1.markdown(f'<div class="stats-card available"><h3>12</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
    c2.markdown(f'<div class="stats-card active"><h3>{active_m}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
    c3.markdown(f'<div class="stats-card completed" style="border-color:#00ffaa;"><h3>{completed_m}</h3><p>DONE</p></div>', unsafe_allow_html=True)

    # 4. MISSIONS
    st.divider()
    m_col1, m_col2 = st.columns(2)

    with m_col1:
        with st.container(border=True):
            st.subheader("🧹 BEACH CLEANUP")
            st.write("Respect Gain: +10")
            if st.button("ACCEPT MISSION"):
                user_db[user_name]["active_missions"] = active_m + 1
                user_db[user_name]["respect"] = min(user_data["respect"] + 10, 100)
                save_data(user_db)
                st.toast("Database Updated!")
                st.rerun()

    with m_col2:
        with st.container(border=True):
            st.subheader("🍔 FOOD DISTRIBUTION")
            st.write("Respect Gain: +5")
            if st.button("COMPLETE MISSION"):
                if active_m > 0:
                    user_db[user_name]["active_missions"] = active_m - 1
                    user_db[user_name]["completed_missions"] = completed_m + 1
                    save_data(user_db)
                    st.rerun()
                else:
                    st.error("No active missions to complete!")