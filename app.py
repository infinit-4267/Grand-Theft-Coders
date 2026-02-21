import streamlit as st
import random
import json
import os
import string
import base64
from PIL import Image, ImageDraw
import streamlit.components.v1 as components
from datetime import datetime

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

def get_rank(respect):
    if respect < 30:
        return "Street Thug"
    elif respect < 60:
        return "Lieutenant"
    elif respect < 85:
        return "Boss"
    else:
        return "Kingpin"

def get_tier(respect):
    if respect < 40:
        return "🥉 Bronze"
    elif respect < 70:
        return "🥈 Silver"
    elif respect < 90:
        return "🥇 Gold"
    else:
        return "💎 Diamond"

# --- THE BACKGROUND FIX ---
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

try:
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
    bg_style = """<style>.stApp { background-color: #0d0221; }</style>"""

st.markdown(bg_style, unsafe_allow_html=True)

# --- NEON CSS ---
st.markdown("""
<style>
    /* HIDE TOOLBAR BUTTONS BUT KEEP THE SPACE */
    #MainMenu { visibility: hidden; }
    [data-testid="stToolbar"] { visibility: hidden; }
    .stAppDeployButton { display: none; }
    
    /* REMOVE TOP PADDING SO CONTENT FILLS FROM THE TOP */
    .stApp > .main .block-container {
        padding-top: 0rem !important;
        margin-top: -80px !important;
    }
    
    html, body, [class*="css"] { color: white; font-family: 'Courier New', Courier, monospace; }
    h1 { color: #ff00aa; text-align: center; font-size: 55px; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }
    h3 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
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
    ... rest of your existing CSS ...
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "page" not in st.session_state:
    st.session_state.page = "Missions"
if "active_crimes" not in st.session_state:
    st.session_state.active_crimes = [
        {"name": "Downtown", "lat": 25.7617, "lng": -80.1918, "type": "Drug Deal"},
        {"name": "Port of Miami", "lat": 25.7705, "lng": -80.1893, "type": "Robbery"}
    ]
if "user_location" not in st.session_state:
    st.session_state.user_location = {"lat": 25.7617, "lng": -80.1918}
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "confirmation_pending" not in st.session_state:
    st.session_state.confirmation_pending = False
if "verification_target" not in st.session_state:
    st.session_state.verification_target = None

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
                users_db[new_user] = {
                    "password": new_pw, 
                    "respect": 50, 
                    "code": code, 
                    "active": 0, 
                    "done": 0, 
                    "active_list": [],
                    "xp": 0,
                    "join_date": datetime.now().strftime("%Y-%m-%d"),
                    "history": []
                }
                save_users(users_db)
                st.success(f"ID {code} ASSIGNED. SWITCH TO LOGIN.")
            elif new_user in users_db:
                st.warning("Operator already exists.")

    st.markdown('</div>', unsafe_allow_html=True)

# --- SCREEN 2: THE MAIN REPUTATION ENGINE ---
else:
    user_data = users_db[st.session_state.current_user]
    
    # Initialize data structures
    if "active_list" not in user_data:
        user_data["active_list"] = []
    if "xp" not in user_data:
        user_data["xp"] = 0
    if "join_date" not in user_data:
        user_data["join_date"] = datetime.now().strftime("%Y-%m-%d")
    if "history" not in user_data:
        user_data["history"] = []

    # Sidebar Navigation & Profile
    st.sidebar.markdown(f"## 👤 {st.session_state.current_user}")
    with st.sidebar.expander("📂 VIEW OPERATOR PROFILE"):
        st.markdown(f"**ID:** `{user_data['code']}`")
        st.markdown(f"**RANK:** {get_rank(user_data['respect'])}")
        st.markdown(f"**RESPECT:** {user_data['respect']}%")
        st.markdown(f"**XP:** {user_data['xp']}")
    
    # Navigation
    st.sidebar.divider()
    st.sidebar.markdown("### 🧭 NAVIGATION")
    page = st.sidebar.radio("SELECT PAGE", ["Missions", "Profile", "Map"], label_visibility="collapsed")
    st.session_state.page = page
    
    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # ==================== MISSIONS PAGE ====================
    if page == "Missions":
        st.markdown("<h1>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)

        # --- SECTION 1: ONGOING OPERATIONS ---
        if user_data["active_list"]:
            st.markdown("### 🚨 ONGOING OPERATIONS")
            for idx, active_m in enumerate(user_data["active_list"]):
                with st.container(border=True):
                    col_info, col_action = st.columns([3, 2])
                    
                    col_info.markdown(f"**{active_m['name']}**")
                    
                    revealed_key = f"revealed_{active_m['pin']}"
                    if revealed_key not in st.session_state:
                        st.session_state[revealed_key] = False

                    if not st.session_state[revealed_key]:
                        btn_col1, btn_col2 = col_action.columns(2)
                        if btn_col1.button("📂 SUBMIT EVIDENCE", key=f"ev_{idx}"):
                            st.session_state[revealed_key] = True
                            st.toast("Evidence Verified. PIN Transmitted.")
                            st.rerun()
                        
                        if btn_col2.button("❌ ABORT", key=f"abort_{idx}"):
                            user_data["active_list"].pop(idx)
                            user_data["respect"] = max(user_data["respect"] - 5, 0)
                            save_users(users_db)
                            st.toast(f"Operation Canceled. -5 Respect.")
                            st.rerun()
                    else:
                        col_info.info(f"🔑 VERIFICATION PIN: {active_m['pin']}")
                        
                        if col_action.button("COMPLETE ✅", key=f"comp_{idx}"):
                            st.session_state.verification_target = idx
                            st.rerun()

            # Dynamic PIN Verification Form
            if st.session_state.verification_target is not None:
                target_idx = st.session_state.verification_target
                target_mission = user_data["active_list"][target_idx]
                
                with st.form("verify_mission"):
                    st.subheader(f"CONFIRM: {target_mission['name']}")
                    input_pin = st.text_input("ENTER 4-DIGIT PIN PROVIDED BY DISPATCH", type="password")
                    
                    if st.form_submit_button("SUBMIT FOR CLEARANCE"):
                        if input_pin == target_mission['pin']:
                            completed = user_data["active_list"].pop(target_idx)
                            user_data["done"] = user_data.get("done", 0) + 1
                            user_data["xp"] = user_data.get("xp", 0) + completed['points']
                            user_data["respect"] = min(user_data["respect"] + completed['points'], 100)
                            user_data["history"].append(f"{completed['name']} - +{completed['points']} XP")
                            
                            save_users(users_db)
                            st.session_state.verification_target = None
                            st.success("✅ VERIFIED. RESPECT & XP UPDATED.")
                            st.rerun()
                        else:
                            st.error("❌ INVALID PIN. AUTHENTICATION FAILED.")
            st.divider()

        # --- STATS ROW ---
        c1, c2, c3 = st.columns(3)
        c1.markdown(f'<div class="stats-card available"><h3>6</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stats-card active"><h3>{len(user_data.get("active_list", []))}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stats-card completed"><h3>{user_data.get("done", 0)}</h3><p>COMPLETED</p></div>', unsafe_allow_html=True)

        # --- SECTION 2: MISSION GRID ---
        st.markdown("### 🎯 AVAILABLE MISSIONS")
        
        mission_data = [
            {
                "name": "BEACH CLEANUP OPERATION",
                "diff": "EASY", "cat": "ENVIRONMENT", "diff_clr": "#00ffaa",
                "brief": "The beaches are getting polluted. We need volunteers to help clean up the shoreline. Bring gloves, bags will be provided.",
                "loc": "Ocean Beach", "time": "2-3 hours", "interested": "34 interested", "award": "Certificate of Appreciation", "pts": 5
            },
            {
                "name": "NEIGHBORHOOD WATCH PATROL",
                "diff": "MEDIUM", "cat": "SAFETY", "diff_clr": "#ffaa00",
                "brief": "Walk through neighborhoods in groups, report suspicious activity, and help residents feel safe. Training provided by local police department.",
                "loc": "Vice Point", "time": "2 hours", "interested": "28 interested", "award": "Safety Certificate", "pts": 8
            },
            {
                "name": "COMMUNITY GARDEN BUILD",
                "diff": "HARD", "cat": "ENVIRONMENT", "diff_clr": "#ff4444",
                "brief": "We're building a garden from scratch! Need volunteers for heavy lifting, carpentry, and planting. All skill levels welcome.",
                "loc": "Little Haiti", "time": "Full Day (6-8 hours)", "interested": "19 interested", "award": "Garden Access Pass", "pts": 15
            },
            {
                "name": "EMERGENCY RESPONSE TRAINING",
                "diff": "MEDIUM", "cat": "SAFETY", "diff_clr": "#ffaa00",
                "brief": "Get certified in life-saving skills! Free training session with professional instructors. Be prepared to help in emergencies.",
                "loc": "Fire Department HQ", "time": "6 hours", "interested": "25 interested", "award": "CPR Certification", "pts": 12
            },
            {
                "name": "STREET FOOD DISTRIBUTION",
                "diff": "EASY", "cat": "COMMUNITY", "diff_clr": "#00ffaa",
                "brief": "Distribute hot meals to homeless community members downtown. Help make a difference in local lives.",
                "loc": "Downtown Vice City", "time": "3-4 hours", "interested": "45 interested", "award": "Community Service Hours", "pts": 5
            },
            {
                "name": "ANIMAL SHELTER SUPPORT",
                "diff": "EASY", "cat": "COMMUNITY", "diff_clr": "#00ffaa",
                "brief": "Our furry friends need love! Help walk dogs, play with cats, and clean kennels at the local shelter.",
                "loc": "Vice City Animal Shelter", "time": "2-3 hours", "interested": "42 interested", "award": "Animal Lover Badge", "pts": 5
            }
        ]

        rows = [mission_data[i:i + 3] for i in range(0, len(mission_data), 3)]
        
        for row_missions in rows:
            cols = st.columns(3)
            for i, m in enumerate(row_missions):
                with cols[i]:
                    st.markdown(f"""
                        <div style="border: 2px solid {m['diff_clr']}; border-radius: 15px; padding: 20px; background: rgba(0, 0, 0, 0.7); min-height: 480px; margin-bottom: 20px;">
                            <div style="margin-bottom: 10px;">
                                <span style="color: {m['diff_clr']}; border: 1px solid {m['diff_clr']}; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">{m['diff']}</span>
                                <span style="color: #00ffff; border: 1px solid #00ffff; padding: 2px 8px; border-radius: 10px; font-size: 10px; font-weight: bold;">{m['cat']}</span>
                            </div>
                            <h4 style="color: white; margin-bottom: 5px; font-family: 'Courier New';">{m['name']}</h4>
                            <div style="background: rgba(255, 0, 170, 0.1); border-left: 3px solid #ff00aa; padding: 10px; margin-bottom: 15px;">
                                <p style="font-size: 11px; line-height: 1.3; color: #eee;">{m['brief']}</p>
                            </div>
                            <p style="font-size: 12px; font-family: 'Courier New';">📍 {m['loc']}<br>⏱️ {m['time']}<br>👥 {m['interested']}<br>🏆 <span style="color: #00ffff;">{m['award']}</span></p>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    is_active = any(act['name'] == m['name'] for act in user_data["active_list"])
                    if is_active:
                        st.warning("📡 IN PROGRESS")
                    elif st.button(f"ACCEPT MISSION", key=f"acc_{m['name']}"):
                        new_pin = "".join(random.choices("0123456789", k=4))
                        user_data["active_list"].append({"name": m['name'], "points": m['pts'], "pin": new_pin})
                        save_users(users_db)
                        st.rerun()

    # ==================== PROFILE PAGE ====================
    elif page == "Profile":
        st.markdown("<h1>👤 OPERATOR PROFILE</h1>", unsafe_allow_html=True)

        level = user_data["xp"] // 100 + 1
        xp_progress = (user_data["xp"] % 100) / 100
        rank = get_rank(user_data["respect"])
        tier = get_tier(user_data["respect"])

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

        st.write("**XP Progress to Next Level:**")
        st.progress(xp_progress)
        st.divider()

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Completed Missions", user_data["done"])
        col2.metric("Active Missions", len(user_data["active_list"]))
        col3.metric("Respect %", user_data["respect"])
        col4.metric("Level", level)

        st.divider()

        st.subheader("🏆 Achievements")

        achievements = []
        if user_data["done"] >= 1:
            achievements.append("🎯 First Mission Completed")
        if user_data["done"] >= 5:
            achievements.append("🔥 5 Missions Completed")
        if user_data["xp"] >= 100:
            achievements.append("⚡ 100 XP Earned")
        if user_data["respect"] >= 80:
            achievements.append("💎 80% Respect Achieved")
        if rank == "Kingpin":
            achievements.append("👑 Kingpin Status")

        if achievements:
            for a in achievements:
                st.success(a)
        else:
            st.info("No achievements unlocked yet.")

        st.divider()

        st.subheader("📜 Mission History")
        if user_data["history"]:
            for h in reversed(user_data["history"][-5:]):
                st.write("✅", h)
        else:
            st.info("No missions completed yet.")

    # ==================== MAP PAGE ====================
    elif page == "Map":
        st.markdown("### 🚨 LIVE CRIMINAL ACTIVITY TRACKER")
        
        col_left, col_right = st.columns([1.2, 2.5])
        
        with col_right:
            st.write("**📍 Use arrow buttons to move your location**")
            
            # Build crimes JSON safely
            crimes_json = json.dumps(st.session_state.active_crimes)
            user_lat = st.session_state.user_location['lat']
            user_lng = st.session_state.user_location['lng']
            
            # Build selected location HTML
            selected_html = ""
            if st.session_state.selected_location:
                sel_lat = st.session_state.selected_location['lat']
                sel_lng = st.session_state.selected_location['lng']
                selected_html = f"""
                L.circleMarker([{sel_lat}, {sel_lng}], {{
                    radius: 11,
                    fillColor: '#00ffff',
                    color: '#fff',
                    weight: 3,
                    opacity: 1,
                    fillOpacity: 0.9
                }}).bindPopup('<b style="color: #00ffff;">🔵 SELECTED</b>').addTo(map).openPopup();
                """
            
            # Create Leaflet map HTML
            map_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css" />
                <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
                <style>
                    body {{ margin: 0; padding: 0; }}
                    #map {{ width: 100%; height: 520px; background: #1a1a1a; }}
                    .leaflet-container {{ background: #1a1a1a !important; }}
                </style>
            </head>
            <body>
                <div id="map"></div>
                <script>
                    var map = L.map('map').setView([25.7617, -80.1918], 11);
                    L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}.png', {{
                        attribution: '© OpenStreetMap',
                        maxZoom: 19
                    }}).addTo(map);
                    
                    // User location (GREEN)
                    L.circleMarker([{user_lat}, {user_lng}], {{
                        radius: 12,
                        fillColor: '#00ff00',
                        color: '#fff',
                        weight: 3,
                        opacity: 1,
                        fillOpacity: 0.9
                    }}).bindPopup('<b style="color: #00ff00;">YOUR LOCATION</b>').addTo(map);
                    
                    // Crime markers
                    var crimes = {crimes_json};
                    var colors = {{
                        'Robbery': '#ff0000',
                        'Grand Theft Auto': '#ff9900',
                        'Drug Deal': '#8000ff',
                        'Vandalism': '#ffff00',
                        'Smuggling': '#0064ff'
                    }};
                    
                    crimes.forEach(function(crime) {{
                        var color = colors[crime.type] || '#ff0000';
                        L.circleMarker([crime.lat, crime.lng], {{
                            radius: 10,
                            fillColor: color,
                            color: '#fff',
                            weight: 2,
                            opacity: 1,
                            fillOpacity: 0.8
                        }}).bindPopup('<b>' + crime.name + '</b><br/>' + crime.type).addTo(map);
                    }});
                    
                    // Selected location
                    {selected_html}
                </script>
            </body>
            </html>
            """
            
            components.html(map_html, height=530)
            
            # Legend
            st.write("**Map Legend:**")
            legend_cols = st.columns(5)
            with legend_cols[0]:
                st.markdown("🟢 Your Location")
            with legend_cols[1]:
                st.markdown("🔴 Robbery")
            with legend_cols[2]:
                st.markdown("🟠 GTA")
            with legend_cols[3]:
                st.markdown("🟣 Drug Deal")
            with legend_cols[4]:
                st.markdown("🟡 Vandalism")
            
            st.divider()
            
            # Direction controls
            st.write("**🎮 Move Your Location (Arrow Controls):**")
            
            dir_col1, dir_col2, dir_col3 = st.columns(3)
            
            with dir_col2:
                if st.button("⬆️ NORTH", use_container_width=True, key="move_north"):
                    st.session_state.user_location['lat'] += 0.002
                    st.rerun()
            
            with dir_col1:
                if st.button("⬅️ WEST", use_container_width=True, key="move_west"):
                    st.session_state.user_location['lng'] -= 0.002
                    st.rerun()
            
            with dir_col3:
                if st.button("➡️ EAST", use_container_width=True, key="move_east"):
                    st.session_state.user_location['lng'] += 0.002
                    st.rerun()
            
            dir_col1, dir_col2, dir_col3 = st.columns(3)
            with dir_col2:
                if st.button("⬇️ SOUTH", use_container_width=True, key="move_south"):
                    st.session_state.user_location['lat'] -= 0.002
                    st.rerun()
            
            st.markdown(f'<div class="user-location-box"><b>🟢 YOUR CURRENT POSITION</b><br/>Lat: {st.session_state.user_location["lat"]:.4f} | Lng: {st.session_state.user_location["lng"]:.4f}</div>', unsafe_allow_html=True)
            
            st.divider()
            
            if st.button("🚨 REPORT AT CURRENT LOCATION", use_container_width=True, key="report_at_location"):
                st.session_state.selected_location = {
                    'lat': st.session_state.user_location['lat'],
                    'lng': st.session_state.user_location['lng']
                }
                st.session_state.confirmation_pending = True
                st.rerun()
        
        with col_left:
            st.write("📋 **DISPATCH CONSOLE**")
            
            c_type = st.selectbox("Crime Type", ["Robbery", "Grand Theft Auto", "Drug Deal", "Vandalism", "Smuggling"], key="crime_type")
            c_name = st.text_input("Incident Location", placeholder="e.g., Downtown Plaza", key="location_name")
            
            st.divider()
            
            if st.session_state.confirmation_pending and st.session_state.selected_location:
                location = st.session_state.selected_location
                
                st.markdown('<div class="confirmation-box">', unsafe_allow_html=True)
                st.markdown("### ✅ CONFIRM LOCATION")
                st.markdown(f"**Latitude:** {location['lat']:.4f}")
                st.markdown(f"**Longitude:** {location['lng']:.4f}")
                st.markdown(f"**Crime Type:** {c_type}")
                st.markdown(f"**Distance:** ~{((((location['lat']-st.session_state.user_location['lat'])**2 + (location['lng']-st.session_state.user_location['lng'])**2)**0.5)*111):.2f}km")
                
                confirm_col1, confirm_col2 = st.columns(2)
                
                with confirm_col1:
                    if st.button("✅ YES, CONFIRM", use_container_width=True, key="confirm_yes"):
                        location_name = c_name if c_name else f"{location['lat']:.4f}, {location['lng']:.4f}"
                        
                        st.session_state.active_crimes.append({
                            "name": location_name,
                            "lat": location['lat'],
                            "lng": location['lng'],
                            "type": c_type
                        })
                        
                        save_users(users_db)
                        st.balloons()
                        st.success(f"✅ {c_type} reported!")
                        
                        st.session_state.selected_location = None
                        st.session_state.confirmation_pending = False
                        st.rerun()
                
                with confirm_col2:
                    if st.button("❌ NO, RESET", use_container_width=True, key="confirm_no"):
                        st.session_state.selected_location = None
                        st.session_state.confirmation_pending = False
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("👆 Move and click REPORT AT CURRENT LOCATION")
            
            st.divider()
            
            if st.button("🧹 CLEAR ALL REPORTS", use_container_width=True, key="clear_btn"):
                st.session_state.active_crimes = []
                st.session_state.selected_location = None
                st.session_state.confirmation_pending = False
                st.rerun()
            
            st.markdown("**📍 ACTIVE INCIDENT REPORTS:**")
            if st.session_state.active_crimes:
                for idx, crime in enumerate(st.session_state.active_crimes, 1):
                    color_emoji = {"Robbery": "🔴", "Grand Theft Auto": "🟠", "Drug Deal": "🟣", "Vandalism": "🟡", "Smuggling": "🔵"}.get(crime['type'], "⚪")
                    distance = (((crime['lat']-st.session_state.user_location['lat'])**2 + (crime['lng']-st.session_state.user_location['lng'])**2)**0.5)*111
                    st.caption(f"{color_emoji} {idx}. {crime['name']} - {crime['type']} ({distance:.1f}km)")
            else:
                st.caption("No active incidents")