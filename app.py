import streamlit as st
import random
import json
import os
import string

# 1. Page Configuration
st.set_page_config(page_title="Vice City Missions", layout="wide")

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

# --- CSS STYLING (Exact Match to Screenshots) ---
st.markdown("""
<style>
    .stApp { background-color: #1a0b2e; color: white; }
    
    /* Header & Subtext */
    .main-title {
        color: #ff00ff; text-align: center; font-size: 50px; font-weight: bold;
        text-shadow: 0 0 10px #ff00ff, 0 0 20px #00ffff; margin-bottom: 0px;
    }
    .sub-text { text-align: center; color: #00ffff; letter-spacing: 2px; font-size: 14px; margin-top: -10px; margin-bottom: 20px;}

    /* Top Alert */
    .alert-box {
        border: 1px solid #ff00aa; border-radius: 8px; padding: 12px;
        text-align: center; color: white; background: rgba(255, 0, 170, 0.1);
        font-size: 13px; margin-bottom: 30px; font-weight: bold;
    }

    /* Stats Cards with Glow */
    .stats-card {
        padding: 25px; border-radius: 15px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.5); transition: 0.3s; height: 160px;
    }
    .available { border-color: #00ffff; box-shadow: 0 0 15px rgba(0, 255, 255, 0.4); }
    .active { border-color: #ff00aa; box-shadow: 0 0 15px rgba(255, 0, 170, 0.4); }
    .completed { border-color: #00ffaa; box-shadow: 0 0 15px rgba(0, 255, 170, 0.4); }

    /* Mission Briefing (The Pink Box) */
    .briefing-box {
        background: rgba(255, 0, 170, 0.12); border-left: 5px solid #ff00aa;
        padding: 15px; margin: 15px 0; font-size: 14px; border-radius: 4px;
        line-height: 1.5; color: #eee;
    }

    /* Badge Styles */
    .badge { padding: 3px 10px; border-radius: 20px; font-size: 11px; font-weight: bold; margin-right: 5px; text-transform: uppercase; }
    .easy-badge { color: #00ffaa; border: 1px solid #00ffaa; }
    .medium-badge { color: #ffaa00; border: 1px solid #ffaa00; }

    /* Sidebar Profile Card */
    .profile-card {
        border: 2px solid #ff00aa; padding: 20px; border-radius: 15px;
        background: rgba(0,0,0,0.6); text-align: center; box-shadow: 0 0 20px rgba(255, 0, 170, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users_db = load_users()

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1 class='main-title'>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        mode = st.radio("SELECT PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
        user_input = st.text_input("OPERATOR ID")
        pw_input = st.text_input("SECURITY CIPHER", type="password")
        if st.button("INITIALIZE SESSION"):
            if user_input in users_db and users_db[user_input]["password"] == pw_input:
                st.session_state.logged_in = True
                st.session_state.current_user = user_input
                st.rerun()
            else: st.error("ACCESS DENIED: Credentials Invalid")

# --- MAIN DASHBOARD (LOGGED IN) ---
else:
    user_name = st.session_state.current_user
    user_data = users_db[user_name]
    
    # --- 1. SIDEBAR PROFILE HUB ---
    with st.sidebar:
        st.markdown(f"""
        <div class="profile-card">
            <h2 style="color:#ff00aa; margin:0;">{user_name.upper()}</h2>
            <p style="color:#00ffff; font-size:12px; margin-bottom:15px;">ID: {user_data.get('code', 'N/A')}</p>
            <hr style="border-color:#444;">
            <p style="text-align:left;"><b>RANK:</b> Street Associate</p>
            <p style="text-align:left;"><b>RESPECT:</b> {user_data.get('respect', 50)}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("")
        if st.button("✅ COMPLETE ACTIVE TASK", help="Click to finish one of your active missions"):
            if user_data.get("active", 0) > 0:
                users_db[user_name]["active"] -= 1
                users_db[user_name]["done"] = user_data.get("done", 0) + 1
                users_db[user_name]["respect"] = min(user_data["respect"] + 5, 100)
                save_users(users_db)
                st.toast("Mission Completed! Respect increased.")
                st.rerun()
            else:
                st.warning("No active missions to complete.")
                
        if st.button("🚪 LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # --- 2. HEADER & STATS ---
    st.markdown("<h1 class='main-title'>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)
    st.markdown("<p class='sub-text'>COMMUNITY MISSIONS · YOUR CHOICE · REAL IMPACT</p>", unsafe_allow_html=True)
    st.markdown("<div class='alert-box'>⚠️ ALL MISSIONS ARE VOLUNTARY · NO PENALTIES FOR DECLINING · YOUR CHOICE MATTERS</div>", unsafe_allow_html=True)

    s1, s2, s3 = st.columns(3)
    with s1:
        st.markdown('<div class="stats-card available"><h1 style="color:#00ffff; margin:0;">12</h1><p>AVAILABLE MISSIONS</p></div>', unsafe_allow_html=True)
    with s2:
        st.markdown(f'<div class="stats-card active"><h1 style="color:#ff00aa; margin:0;">{user_data.get("active", 0)}</h1><p>ACTIVE MISSIONS</p></div>', unsafe_allow_html=True)
    with s3:
        st.markdown(f'<div class="stats-card completed"><h1 style="color:#00ffaa; margin:0;">{user_data.get("done", 0)}</h1><p>COMPLETED MISSIONS</p></div>', unsafe_allow_html=True)

    # --- 3. CATEGORIES ---
    st.markdown("<h3 style='margin-top:40px;'>⭐ MISSION CATEGORIES</h3>", unsafe_allow_html=True)
    c_cols = st.columns(6)
    c_list = ["ALL MISSIONS", "COMMUNITY", "ENVIRONMENT", "EDUCATION", "SAFETY", "HEALTH"]
    for i, name in enumerate(c_list):
        c_cols[i].button(name, key=f"cat_{name}")

    # --- 4. MISSION GRID ---
    st.markdown("<h2 style='color:#00ffff; margin-top:30px;'>🎯 AVAILABLE MISSIONS</h2>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)

    def draw_mission(col, title, tag, diff, briefing, loc, time, ppl, reward, btn_id):
        badge_class = "easy-badge" if diff == "EASY" else "medium-badge"
        with col:
            with st.container(border=True):
                st.markdown(f"<span class='badge {badge_class}'>{diff}</span> <small style='color:#ccc;'>{tag}</small>", unsafe_allow_html=True)
                st.subheader(title)
                st.write(f"Objective: {briefing[:50]}...") # Short intro
                
                st.markdown(f"""
                <div class="briefing-box">
                    <b>MISSION BRIEFING:</b><br>
                    {briefing}
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"📍 **{loc}**")
                st.markdown(f"⏱ **{time}**")
                st.markdown(f"👥 **{ppl} interested**")
                st.markdown(f"🏆 **{reward}**")
                
                if st.button("ACCEPT MISSION", key=btn_id, use_container_width=True):
                    users_db[user_name]["active"] = user_data.get("active", 0) + 1
                    save_users(users_db)
                    st.toast(f"Accepted: {title}")
                    st.rerun()

    draw_mission(m1, "BEACH CLEANUP OPERATION", "ENVIRONMENT", "EASY", 
                 "The beaches are getting polluted. We need volunteers to help clean up the shoreline. Bring gloves, bags will be provided. Let's make Vice City beaches beautiful again!", 
                 "Ocean Beach", "2-3 hours", "34", "Certificate of Appreciation", "m1_acc")

    draw_mission(m2, "STREET FOOD DISTRIBUTION", "COMMUNITY", "EASY", 
                 "Every Saturday, we distribute hot meals to those in need. Join us in making a difference. All food safety protocols followed.", 
                 "Downtown Vice City", "3-4 hours", "45", "Community Service Hours", "m2_acc")

    draw_mission(m3, "YOUTH CODING WORKSHOP", "EDUCATION", "MEDIUM", 
                 "Share your tech knowledge with the next generation. Help teenagers learn coding basics. No teaching experience required, just patience and enthusiasm!", 
                 "Community Tech Center", "4 hours", "12", "Mentor Recognition Badge", "m3_acc")