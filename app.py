import streamlit as st
import random
import json
import os
import string
import base64
from PIL import Image, ImageDraw
import pandas as pd
import streamlit.components.v1 as components

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
    .stats-card {
        padding: 20px; border-radius: 10px; text-align: center; border: 2px solid;
        background: rgba(0,0,0,0.6); backdrop-filter: blur(8px);
    }
    .available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
    .active { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
    .completed { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }
    .badge { padding: 2px 8px; border-radius: 20px; font-size: 12px; border: 1px solid; }
    .easy { color: #00ffaa; border-color: #00ffaa; }
    .medium { color: #ffaa00; border-color: #ffaa00; }
    div.stButton > button {
        background-color: black; color: #00ffff; border: 2px solid #ff00aa;
        border-radius: 10px; font-weight: bold; width: 100%; height: 45px;
    }
    div.stButton > button:hover {
        background-color: #ff00aa; color: white; box-shadow: 0 0 20px #ff00aa;
    }
    .confirmation-box {
        padding: 20px;
        border: 2px solid #00ffff;
        border-radius: 10px;
        background-color: rgba(0, 20, 40, 0.9);
        box-shadow: 0 0 20px #00ffff;
        margin: 10px 0;
    }
    .user-location-box {
        padding: 15px;
        border: 2px solid #00ff00;
        border-radius: 10px;
        background-color: rgba(0, 40, 0, 0.9);
        box-shadow: 0 0 15px #00ff00;
        margin: 10px 0;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "active_crimes" not in st.session_state:
    st.session_state.active_crimes = [
        {"name": "Downtown Miami", "lat": 25.7617, "lng": -80.1918, "type": "Drug Deal"},
        {"name": "Port of Miami", "lat": 25.7705, "lng": -80.1893, "type": "Robbery"}
    ]
if "user_location" not in st.session_state:
    st.session_state.user_location = {"lat": 25.7617, "lng": -80.1918}
if "selected_location" not in st.session_state:
    st.session_state.selected_location = None
if "confirmation_pending" not in st.session_state:
    st.session_state.confirmation_pending = False

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

    # --- INTERACTIVE MAP DISPLAY ---
    st.divider()
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
                    'Natural Disaster': '#0064ff'
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
        
        c_type = st.selectbox("Crime Type", ["Robbery", "Grand Theft Auto", "Drug Deal", "Vandalism", "Natural Disaster"], key="crime_type")
        c_name = st.text_input("Location Name (optional)", placeholder="e.g., Downtown Plaza", key="location_name")
        
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
                color_emoji = {"Robbery": "🔴", "Grand Theft Auto": "🟠", "Drug Deal": "🟣", "Vandalism": "🟡", "Natural Disaster": "🔵"}.get(crime['type'], "⚪")
                distance = (((crime['lat']-st.session_state.user_location['lat'])**2 + (crime['lng']-st.session_state.user_location['lng'])**2)**0.5)*111
                st.caption(f"{color_emoji} {idx}. {crime['name']} - {crime['type']} ({distance:.1f}km)")
        else:
            st.caption("No active incidents")