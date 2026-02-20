import streamlit as st
import random
import json
import os
import string
from PIL import Image, ImageDraw

# 1. Page Configuration
st.set_page_config(page_title="Vice City Intelligence", layout="wide")

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

# --- CSS STYLING (The Neon Briefing Look) ---
st.markdown("""
<style>
    .stApp { background-color: #0d0221; color: white; }
    h1 { color: #ff00aa; text-align: center; text-shadow: 0 0 10px #ff00aa, 0 0 20px #00ffff; }
    
    /* Stats Cards */
    .stats-card {
        padding: 25px; border-radius: 15px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.5); height: 160px;
    }
    .available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
    .active { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
    .completed { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }

    /* Mission Briefing (Pink Box) */
    .briefing-box {
        background: rgba(255, 0, 170, 0.12); border-left: 5px solid #ff00aa;
        padding: 15px; margin: 15px 0; font-size: 14px; border-radius: 4px;
    }

    /* Buttons */
    div.stButton > button {
        background-color: black; color: #00ffff; border: 2px solid #ff00aa;
        border-radius: 10px; font-weight: bold; width: 100%;
    }
    
    .profile-card {
        border: 2px solid #ff00aa; padding: 20px; border-radius: 15px;
        background: rgba(0,0,0,0.6); text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

users_db = load_users()

# --- LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
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
            else: st.error("ACCESS DENIED")
        else:
            if mode == "CREATE ACCOUNT":
                new_user = st.text_input("CHOOSE OPERATOR NAME", key="new_user")
                new_pw = st.text_input("SET CIPHER", type="password", key="new_pw")
                if st.button("GENERATE ID & REGISTER"):
                    if new_user and new_pw and new_user not in users_db:
                        code = generate_account_code()
                        users_db[new_user] = {"password": new_pw, "respect": 50, "code": code, "active": 0, "done": 0, "reports": []}
                        save_users(users_db)
                        st.success(f"ID GENERATED: {code}")

# --- MAIN ENGINE ---
else:
    user_name = st.session_state.current_user
    user_data = users_db[user_name]
    
    # 1. SIDEBAR PROFILE HUB
    with st.sidebar:
        st.markdown(f"""
        <div class="profile-card">
            <h2 style="color:#ff00aa; margin:0;">{user_name.upper()}</h2>
            <p style="color:#00ffff; font-size:12px;">ID: {user_data.get('code', 'N/A')}</p>
            <hr>
            <p style="text-align:left;"><b>RANK:</b> Street Associate</p>
            <p style="text-align:left;"><b>RESPECT:</b> {user_data.get('respect', 50)}%</p>
        </div>
        """, unsafe_allow_html=True)
        
        # New: View Past Reports in Sidebar
        with st.expander("📜 MY INTEL LOGS"):
            reports = user_data.get("reports", [])
            if reports:
                for r in reports:
                    st.markdown(f"📍 **{r['district']}**\n- {r['type']}")
            else:
                st.write("No reports filed yet.")
        
        st.divider()
        if st.button("LOGOUT"):
            st.session_state.logged_in = False
            st.rerun()

    # 2. DASHBOARD HEADER
    st.markdown("<h1>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:#00ffff;'>COMMUNITY MISSIONS · YOUR CHOICE · REAL IMPACT</p>", unsafe_allow_html=True)
    st.info("⚠️ ALL MISSIONS ARE VOLUNTARY · YOUR CHOICE MATTERS")

    # 3. STATS ROW
    s1, s2, s3 = st.columns(3)
    s1.markdown('<div class="stats-card available"><h1 style="color:#00ffff; margin:0;">12</h1><p>AVAILABLE</p></div>', unsafe_allow_html=True)
    s2.markdown(f'<div class="stats-card active"><h1 style="color:#ff00aa; margin:0;">{user_data.get("active", 0)}</h1><p>ACTIVE</p></div>', unsafe_allow_html=True)
    s3.markdown(f'<div class="stats-card completed"><h1 style="color:#00ffaa; margin:0;">{user_data.get("done", 0)}</h1><p>COMPLETED</p></div>', unsafe_allow_html=True)

    # 4. REPORT A CRIME
    st.divider()
    st.markdown("### 🚨 REPORT CRIMINAL ACTIVITY")
    with st.container(border=True):
        crime_col1, crime_col2 = st.columns(2)
        with crime_col1:
            report_district = st.selectbox("Incident Location", ["Downtown", "Ocean Beach", "Little Havana", "Vice Point", "Port of Miami"])
            report_type = st.selectbox("Crime Type", ["Vandalism", "Theft", "Suspicious Activity", "Street Racing", "Smuggling"])
        with crime_col2:
            report_details = st.text_area("Intel Details", placeholder="What did you see, operator?")
            if st.button("SUBMIT REPORT TO VERCETTI BUREAU"):
                if report_details:
                    new_report = {"district": report_district, "type": report_type, "details": report_details}
                    if "reports" not in users_db[user_name]:
                        users_db[user_name]["reports"] = []
                    users_db[user_name]["reports"].append(new_report)
                    users_db[user_name]["respect"] = min(user_data["respect"] + 2, 100) # Loyalty bonus
                    save_users(users_db)
                    st.toast("Intel Submitted! Respect +2")
                    st.rerun()
                else:
                    st.error("Briefing details required for processing.")

    # 5. MISSION GRID
    st.markdown("<h2 style='color:#00ffff; margin-top:30px;'>🎯 AVAILABLE MISSIONS</h2>", unsafe_allow_html=True)
    m1, m2, m3 = st.columns(3)

    def draw_mission(col, title, tag, diff, briefing, loc, time, ppl, key):
        with col:
            with st.container(border=True):
                st.markdown(f"<span style='color:#00ffaa; border:1px solid #00ffaa; padding:2px 8px; border-radius:10px; font-size:10px;'>{diff}</span> <small>{tag}</small>", unsafe_allow_html=True)
                st.subheader(title)
                st.markdown(f"<div class='briefing-box'><b>MISSION BRIEFING:</b><br>{briefing}</div>", unsafe_allow_html=True)
                st.markdown(f"📍 **{loc}** | ⏱ **{time}** | 👥 **{ppl} interested**")
                if st.button("ACCEPT MISSION", key=key):
                    users_db[user_name]["active"] += 1
                    save_users(users_db)
                    st.rerun()

    draw_mission(m1, "BEACH CLEANUP", "ENVIRONMENT", "EASY", "Shoreline pollution is peaking. Help us clear the sands.", "Ocean Beach", "2h", "34", "m1_rep")
    draw_mission(m2, "FOOD DISTRIBUTION", "COMMUNITY", "EASY", "Help serve meals to the downtown community.", "Downtown", "3h", "45", "m2_rep")
    draw_mission(m3, "CODING WORKSHOP", "EDUCATION", "MEDIUM", "Mentor local teens in basic Python logic.", "Tech Center", "4h", "12", "m3_rep")

# Note: Ensure you have a 'map.jpg' in your directory for the Tactical Map feature.