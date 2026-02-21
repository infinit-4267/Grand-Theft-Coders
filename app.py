import streamlit as st
import random
import json
import os
import string
import base64
import math
import streamlit.components.v1 as components
from datetime import datetime

# ─────────────────────────────────────────────
# 1. Page Configuration
# ─────────────────────────────────────────────
st.set_page_config(page_title="Vice City Reputation Engine", layout="wide")

# ─────────────────────────────────────────────
# 2. DATABASE HELPERS
# ─────────────────────────────────────────────
DB_FILE      = "users.json"
INCIDENT_FILE = "incidents.json"

def load_users():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return {}

def save_users(users):
    with open(DB_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_incidents():
    if os.path.exists(INCIDENT_FILE):
        with open(INCIDENT_FILE, "r") as f:
            content = f.read().strip()
            if content:
                return json.loads(content)
    return []

def save_incidents(incidents):
    with open(INCIDENT_FILE, "w") as f:
        json.dump(incidents, f, indent=4)

def generate_account_code():
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# ─────────────────────────────────────────────
# 3. RANK / TIER / TRUST HELPERS
# ─────────────────────────────────────────────
def get_rank(respect):
    if respect < 30:  return "Street Thug"
    elif respect < 60: return "Lieutenant"
    elif respect < 85: return "Boss"
    else:              return "Kingpin"

def get_tier(respect):
    if respect < 40:  return "🥉 Bronze"
    elif respect < 70: return "🥈 Silver"
    elif respect < 90: return "🥇 Gold"
    else:              return "💎 Diamond"

def get_trust_label(trust):
    if trust >= 75:   return ("🟢 TRUSTED",    "#00ff88")
    elif trust >= 45: return ("🟡 NEUTRAL",    "#ffcc00")
    else:             return ("🔴 SUSPICIOUS", "#ff4444")

def get_truth_index(incident):
    """Weighted truth index: each vote is weighted by voter's trust factor."""
    votes = incident.get("votes", {})
    if not votes:
        return 50  # default neutral
    real_weight = 0
    fake_weight = 0
    for voter, data in votes.items():
        w = data.get("trust_at_vote", 50) / 100
        if data["vote"] == "real":
            real_weight += w
        else:
            fake_weight += w
    total = real_weight + fake_weight
    if total == 0:
        return 50
    return round((real_weight / total) * 100)

def haversine_km(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlng/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))

def users_in_radius(incident, users_db, radius_km=2.0):
    """Return list of usernames whose last-known location is within radius_km of the incident."""
    nearby = []
    for uname, udata in users_db.items():
        loc = udata.get("last_location")
        if loc:
            d = haversine_km(incident["lat"], incident["lng"], loc["lat"], loc["lng"])
            if d <= radius_km:
                nearby.append(uname)
    return nearby

# ─────────────────────────────────────────────
# 4. BACKGROUND + CSS
# ─────────────────────────────────────────────
def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

try:
    bin_str = get_base64('background.png')
    bg_style = f"""
    <style>
    .stApp {{
        background-image: linear-gradient(rgba(0,0,0,0.6),rgba(0,0,0,0.6)),url("data:image/png;base64,{bin_str}");
        background-size: cover; background-position: center; background-attachment: fixed;
    }}
    header[data-testid="stHeader"] {{ background: rgba(0,0,0,0) !important; }}
    </style>"""
except:
    bg_style = """<style>.stApp { background-color: #0d0221; }</style>"""

st.markdown(bg_style, unsafe_allow_html=True)

st.markdown("""
<style>
html, body, [class*="css"] { color: white; font-family: 'Courier New', Courier, monospace; }
h1 { color: #ff00aa; text-align: center; font-size: 50px; text-shadow: 0 0 20px #ff00aa, 0 0 40px #00ffff; }
h3 { color: #00ffff; text-shadow: 0 0 10px #00ffff; }
.login-box {
    padding: 40px; border: 2px solid #00ffff; border-radius: 20px;
    background-color: rgba(15,15,15,0.85); backdrop-filter: blur(12px);
    box-shadow: 0 0 30px #00ffff; max-width: 500px; margin: auto;
}
.stats-card { padding: 20px; border-radius: 10px; text-align: center; border: 2px solid; background: rgba(0,0,0,0.6); backdrop-filter: blur(8px); }
.available { border-color: #00ffff; box-shadow: 0 0 10px #00ffff; }
.active    { border-color: #ff00aa; box-shadow: 0 0 10px #ff00aa; }
.completed { border-color: #00ffaa; box-shadow: 0 0 10px #00ffaa; }
.trust-box {
    padding: 15px; border-radius: 10px; background: rgba(0,0,0,0.7);
    border: 2px solid; margin: 8px 0; font-family: 'Courier New';
}
.confirmation-box {
    padding: 20px; border: 2px solid #00ffff; border-radius: 10px;
    background-color: rgba(0,20,40,0.9); box-shadow: 0 0 20px #00ffff; margin: 10px 0;
}
.user-location-box {
    padding: 15px; border: 2px solid #00ff00; border-radius: 10px;
    background-color: rgba(0,40,0,0.9); box-shadow: 0 0 15px #00ff00;
    margin: 10px 0; text-align: center;
}
div.stButton > button {
    background-color: black; color: #00ffff; border: 2px solid #ff00aa;
    border-radius: 10px; font-weight: bold; width: 100%; height: 45px;
}
div.stButton > button:hover { background-color: #ff00aa; color: white; box-shadow: 0 0 20px #ff00aa; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 5. SESSION STATE INIT
# ─────────────────────────────────────────────
for key, default in {
    "logged_in": False,
    "page": "Missions",
    "user_location": {"lat": 25.7617, "lng": -80.1918},
    "selected_location": None,
    "confirmation_pending": False,
    "verification_target": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

users_db  = load_users()
incidents = load_incidents()

# ─────────────────────────────────────────────
# 6. LOGIN / SIGNUP SCREEN
# ─────────────────────────────────────────────
if not st.session_state.logged_in:
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)

    mode = st.radio("SELECT PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)

    if mode == "LOGIN":
        user_input = st.text_input("OPERATOR ID")
        pw_input   = st.text_input("SECURITY CIPHER", type="password")
        if st.button("INITIALIZE SESSION"):
            if user_input in users_db and users_db[user_input]["password"] == pw_input:
                st.session_state.logged_in      = True
                st.session_state.current_user   = user_input
                st.rerun()
            else:
                st.error("ACCESS DENIED: Cipher Mismatch")
    else:
        new_user = st.text_input("CHOOSE OPERATOR NAME")
        new_pw   = st.text_input("SET CIPHER", type="password")
        if st.button("GENERATE ID & REGISTER"):
            if new_user and new_pw and new_user not in users_db:
                code = generate_account_code()
                users_db[new_user] = {
                    "password":      new_pw,
                    "respect":       50,
                    "code":          code,
                    "active":        0,
                    "done":          0,
                    "active_list":   [],
                    "xp":            0,
                    "trust_factor":  50,          # ← NEW: starts neutral
                    "verifications": 0,           # total votes cast
                    "correct_verifications": 0,   # votes that matched consensus
                    "join_date":     datetime.now().strftime("%Y-%m-%d"),
                    "history":       [],
                    "last_location": {"lat": 25.7617, "lng": -80.1918}
                }
                save_users(users_db)
                st.success(f"ID {code} ASSIGNED. SWITCH TO LOGIN.")
            elif new_user in users_db:
                st.warning("Operator already exists.")
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 7. MAIN APP
# ─────────────────────────────────────────────
else:
    user_data = users_db[st.session_state.current_user]
    current_user = st.session_state.current_user

    # Back-fill missing fields for old accounts
    for field, val in [("active_list", []), ("xp", 0), ("join_date", datetime.now().strftime("%Y-%m-%d")),
                       ("history", []), ("trust_factor", 50), ("verifications", 0),
                       ("correct_verifications", 0), ("last_location", {"lat": 25.7617, "lng": -80.1918})]:
        if field not in user_data:
            user_data[field] = val

    trust_label, trust_color = get_trust_label(user_data["trust_factor"])

    # ── Sidebar ──────────────────────────────
    st.sidebar.markdown(f"## 👤 {current_user}")
    with st.sidebar.expander("📂 VIEW OPERATOR PROFILE"):
        st.markdown(f"**ID:** `{user_data['code']}`")
        st.markdown(f"**RANK:** {get_rank(user_data['respect'])}")
        st.markdown(f"**RESPECT:** {user_data['respect']}%")
        st.markdown(f"**XP:** {user_data['xp']}")
        st.markdown(f"**TRUST:** <span style='color:{trust_color};font-weight:bold'>{trust_label} ({user_data['trust_factor']}/100)</span>", unsafe_allow_html=True)

    st.sidebar.divider()
    st.sidebar.markdown("### 🧭 NAVIGATION")
    page = st.sidebar.radio("SELECT PAGE", ["Missions", "Profile", "Map", "Incidents"], label_visibility="collapsed")
    st.session_state.page = page

    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.rerun()

    # ══════════════════════════════════════════
    # PAGE: MISSIONS
    # ══════════════════════════════════════════
    if page == "Missions":
        st.markdown("<h1>🎯 VICE CITY MISSIONS</h1>", unsafe_allow_html=True)

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
                        b1, b2 = col_action.columns(2)
                        if b1.button("📂 SUBMIT EVIDENCE", key=f"ev_{idx}"):
                            st.session_state[revealed_key] = True
                            st.toast("Evidence Verified. PIN Transmitted.")
                            st.rerun()
                        if b2.button("❌ ABORT", key=f"abort_{idx}"):
                            user_data["active_list"].pop(idx)
                            user_data["respect"] = max(user_data["respect"] - 5, 0)
                            save_users(users_db)
                            st.rerun()
                    else:
                        col_info.info(f"🔑 VERIFICATION PIN: {active_m['pin']}")
                        if col_action.button("COMPLETE ✅", key=f"comp_{idx}"):
                            st.session_state.verification_target = idx
                            st.rerun()

            if st.session_state.verification_target is not None:
                target_idx = st.session_state.verification_target
                target_mission = user_data["active_list"][target_idx]
                with st.form("verify_mission"):
                    st.subheader(f"CONFIRM: {target_mission['name']}")
                    input_pin = st.text_input("ENTER 4-DIGIT PIN", type="password")
                    if st.form_submit_button("SUBMIT FOR CLEARANCE"):
                        if input_pin == target_mission['pin']:
                            completed = user_data["active_list"].pop(target_idx)
                            user_data["done"]    = user_data.get("done", 0) + 1
                            user_data["xp"]      = user_data.get("xp", 0) + completed['points']
                            user_data["respect"] = min(user_data["respect"] + completed['points'], 100)
                            user_data["history"].append(f"{completed['name']} - +{completed['points']} XP")
                            save_users(users_db)
                            st.session_state.verification_target = None
                            st.success("✅ VERIFIED. RESPECT & XP UPDATED.")
                            st.rerun()
                        else:
                            st.error("❌ INVALID PIN.")
            st.divider()

        c1, c2, c3 = st.columns(3)
        c1.markdown('<div class="stats-card available"><h3>6</h3><p>AVAILABLE</p></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="stats-card active"><h3>{len(user_data.get("active_list",[]))}</h3><p>ACTIVE</p></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="stats-card completed"><h3>{user_data.get("done",0)}</h3><p>COMPLETED</p></div>', unsafe_allow_html=True)

        st.markdown("### 🎯 AVAILABLE MISSIONS")
        mission_data = [
            {"name":"BEACH CLEANUP OPERATION","diff":"EASY","cat":"ENVIRONMENT","diff_clr":"#00ffaa","brief":"Clean up the shoreline. Bring gloves, bags provided.","loc":"Ocean Beach","time":"2-3 hours","interested":"34 interested","award":"Certificate of Appreciation","pts":5},
            {"name":"NEIGHBORHOOD WATCH PATROL","diff":"MEDIUM","cat":"SAFETY","diff_clr":"#ffaa00","brief":"Walk neighborhoods, report suspicious activity. Training provided.","loc":"Vice Point","time":"2 hours","interested":"28 interested","award":"Safety Certificate","pts":8},
            {"name":"COMMUNITY GARDEN BUILD","diff":"HARD","cat":"ENVIRONMENT","diff_clr":"#ff4444","brief":"Build a garden from scratch. Heavy lifting & planting.","loc":"Little Haiti","time":"Full Day","interested":"19 interested","award":"Garden Access Pass","pts":15},
            {"name":"EMERGENCY RESPONSE TRAINING","diff":"MEDIUM","cat":"SAFETY","diff_clr":"#ffaa00","brief":"Free CPR & emergency training with professional instructors.","loc":"Fire Department HQ","time":"6 hours","interested":"25 interested","award":"CPR Certification","pts":12},
            {"name":"STREET FOOD DISTRIBUTION","diff":"EASY","cat":"COMMUNITY","diff_clr":"#00ffaa","brief":"Distribute hot meals to homeless community members downtown.","loc":"Downtown Vice City","time":"3-4 hours","interested":"45 interested","award":"Community Service Hours","pts":5},
            {"name":"ANIMAL SHELTER SUPPORT","diff":"EASY","cat":"COMMUNITY","diff_clr":"#00ffaa","brief":"Walk dogs, play with cats, clean kennels at the local shelter.","loc":"Vice City Animal Shelter","time":"2-3 hours","interested":"42 interested","award":"Animal Lover Badge","pts":5},
        ]
        rows = [mission_data[i:i+3] for i in range(0, len(mission_data), 3)]
        for row_missions in rows:
            cols = st.columns(3)
            for i, m in enumerate(row_missions):
                with cols[i]:
                    st.markdown(f"""
                    <div style="border:2px solid {m['diff_clr']};border-radius:15px;padding:20px;background:rgba(0,0,0,0.7);min-height:440px;margin-bottom:20px;">
                        <span style="color:{m['diff_clr']};border:1px solid {m['diff_clr']};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:bold;">{m['diff']}</span>
                        <span style="color:#00ffff;border:1px solid #00ffff;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:bold;">{m['cat']}</span>
                        <h4 style="color:white;margin:8px 0;font-family:'Courier New';">{m['name']}</h4>
                        <div style="background:rgba(255,0,170,0.1);border-left:3px solid #ff00aa;padding:10px;margin-bottom:15px;">
                            <p style="font-size:11px;line-height:1.3;color:#eee;">{m['brief']}</p>
                        </div>
                        <p style="font-size:12px;">📍 {m['loc']}<br>⏱️ {m['time']}<br>👥 {m['interested']}<br>🏆 <span style="color:#00ffff;">{m['award']}</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    is_active = any(a['name'] == m['name'] for a in user_data["active_list"])
                    if is_active:
                        st.warning("📡 IN PROGRESS")
                    elif st.button("ACCEPT MISSION", key=f"acc_{m['name']}"):
                        new_pin = "".join(random.choices("0123456789", k=4))
                        user_data["active_list"].append({"name": m['name'], "points": m['pts'], "pin": new_pin})
                        save_users(users_db)
                        st.rerun()

    # ══════════════════════════════════════════
    # PAGE: PROFILE
    # ══════════════════════════════════════════
    elif page == "Profile":
        st.markdown("<h1>👤 OPERATOR PROFILE</h1>", unsafe_allow_html=True)

        level       = user_data["xp"] // 100 + 1
        xp_progress = (user_data["xp"] % 100) / 100
        rank        = get_rank(user_data["respect"])
        tier        = get_tier(user_data["respect"])
        tf          = user_data["trust_factor"]
        tl, tc      = get_trust_label(tf)
        verif_total = user_data.get("verifications", 0)
        correct     = user_data.get("correct_verifications", 0)
        accuracy    = f"{round(correct/verif_total*100)}%" if verif_total else "N/A"

        st.markdown(f"""
        <div class="login-box">
            <h3>ID: {user_data['code']}</h3>
            <h3>Rank: {rank} | Tier: {tier}</h3>
            <h3>Level: {level} | Respect: {user_data['respect']}%</h3>
            <h3>Total XP: {user_data['xp']}</h3>
            <h3>Joined: {user_data['join_date']}</h3>
            <hr style="border-color:#00ffff55;">
            <h3>Trust Factor: <span style="color:{tc};">{tl} ({tf}/100)</span></h3>
            <p style="font-size:13px;color:#aaa;">Verifications Cast: {verif_total} | Accuracy: {accuracy}</p>
        </div>
        """, unsafe_allow_html=True)

        st.write("**XP Progress to Next Level:**")
        st.progress(xp_progress)
        st.write("**Trust Factor:**")
        st.progress(tf / 100)

        st.divider()

        col1, col2, col3, col4, col5 = st.columns(5)
        col1.metric("Completed", user_data["done"])
        col2.metric("Active", len(user_data["active_list"]))
        col3.metric("Respect %", user_data["respect"])
        col4.metric("Level", level)
        col5.metric("Trust", f"{tf}/100")

        st.divider()
        st.subheader("🏆 Achievements")
        achievements = []
        if user_data["done"] >= 1:          achievements.append("🎯 First Mission Completed")
        if user_data["done"] >= 5:          achievements.append("🔥 5 Missions Completed")
        if user_data["xp"] >= 100:          achievements.append("⚡ 100 XP Earned")
        if user_data["respect"] >= 80:      achievements.append("💎 80% Respect Achieved")
        if rank == "Kingpin":               achievements.append("👑 Kingpin Status")
        if tf >= 75:                        achievements.append("🟢 Trusted Operator")
        if verif_total >= 10:               achievements.append("🔍 10 Incidents Verified")
        if achievements:
            for a in achievements: st.success(a)
        else:
            st.info("No achievements unlocked yet.")

        st.divider()
        st.subheader("📜 Mission History")
        if user_data["history"]:
            for h in reversed(user_data["history"][-5:]): st.write("✅", h)
        else:
            st.info("No missions completed yet.")

    # ══════════════════════════════════════════
    # PAGE: MAP
    # ══════════════════════════════════════════
    elif page == "Map":
        st.markdown("<h1>🗺️ LIVE INCIDENT MAP</h1>", unsafe_allow_html=True)

        col_left, col_right = st.columns([1.2, 2.5])
        VERIFY_RADIUS_KM = 2.0

        with col_right:
            st.write("**📍 Move your location with arrow buttons**")

            user_lat = st.session_state.user_location['lat']
            user_lng = st.session_state.user_location['lng']

            # Build incident circles + markers
            incident_js = ""
            for inc in incidents:
                truth = get_truth_index(inc)
                votes = inc.get("votes", {})
                vote_count = len(votes)
                real_votes = sum(1 for v in votes.values() if v["vote"] == "real")
                fake_votes = vote_count - real_votes
                if truth >= 70:   circle_color = "#00ff88"
                elif truth >= 40: circle_color = "#ffcc00"
                else:             circle_color = "#ff4444"
                crime_colors = {"Robbery":"#ff0000","Grand Theft Auto":"#ff9900","Drug Deal":"#8000ff","Vandalism":"#ffff00","Smuggling":"#0064ff"}
                marker_color = crime_colors.get(inc.get("type",""), "#ff0000")
                safe_name = inc['name'].replace("'", "\\'")
                incident_js += f"""
                L.circle([{inc['lat']}, {inc['lng']}], {{
                    radius: {VERIFY_RADIUS_KM * 1000},
                    color: '{circle_color}',
                    fillColor: '{circle_color}',
                    fillOpacity: 0.08,
                    weight: 2,
                    dashArray: '6 4'
                }}).bindTooltip('Truth Index: {truth}%  ({real_votes}✅ / {fake_votes}❌)', {{permanent: false}}).addTo(map);
                L.circleMarker([{inc['lat']}, {inc['lng']}], {{
                    radius: 10,
                    fillColor: '{marker_color}',
                    color: '#fff',
                    weight: 2, opacity: 1, fillOpacity: 0.9
                }}).bindPopup('<b style="font-family:monospace">{safe_name}</b><br/>{inc.get("type","Unknown")}<br/>Truth: {truth}%<br/>Votes: {vote_count}').addTo(map);
                """

            selected_html = ""
            if st.session_state.selected_location:
                sl = st.session_state.selected_location
                selected_html = f"""
                L.circleMarker([{sl['lat']}, {sl['lng']}], {{
                    radius: 11, fillColor: '#00ffff', color: '#fff',
                    weight: 3, opacity: 1, fillOpacity: 0.9
                }}).bindPopup('<b style="color:#00ffff;">🔵 SELECTED</b>').addTo(map).openPopup();
                """

            map_html = f"""
            <!DOCTYPE html><html><head>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.css"/>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/leaflet.min.js"></script>
            <style>body{{margin:0;padding:0;}} #map{{width:100%;height:520px;background:#1a1a1a;}}</style>
            </head><body><div id="map"></div>
            <script>
            var map = L.map('map').setView([25.7617,-80.1918],11);
            L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}.png',{{attribution:'©OSM',maxZoom:19}}).addTo(map);
            L.circleMarker([{user_lat},{user_lng}],{{radius:12,fillColor:'#00ff00',color:'#fff',weight:3,opacity:1,fillOpacity:0.9}}).bindPopup('<b style="color:#00ff00;">YOUR LOCATION</b>').addTo(map);
            {incident_js}
            {selected_html}
            </script></body></html>
            """
            components.html(map_html, height=530)

            st.markdown("**Legend:** 🟢 Your Location &nbsp; | &nbsp; Dashed circle = 2km verify radius &nbsp; | &nbsp; Circle color: 🟢 High Truth / 🟡 Uncertain / 🔴 Low Truth")
            st.divider()

            dir_col1, dir_col2, dir_col3 = st.columns(3)
            with dir_col2:
                if st.button("⬆️ NORTH", use_container_width=True):
                    st.session_state.user_location['lat'] += 0.002
                    users_db[current_user]["last_location"] = dict(st.session_state.user_location)
                    save_users(users_db)
                    st.rerun()
            with dir_col1:
                if st.button("⬅️ WEST",  use_container_width=True):
                    st.session_state.user_location['lng'] -= 0.002
                    users_db[current_user]["last_location"] = dict(st.session_state.user_location)
                    save_users(users_db)
                    st.rerun()
            with dir_col3:
                if st.button("➡️ EAST",  use_container_width=True):
                    st.session_state.user_location['lng'] += 0.002
                    users_db[current_user]["last_location"] = dict(st.session_state.user_location)
                    save_users(users_db)
                    st.rerun()
            dir_col1, dir_col2, dir_col3 = st.columns(3)
            with dir_col2:
                if st.button("⬇️ SOUTH", use_container_width=True):
                    st.session_state.user_location['lat'] -= 0.002
                    users_db[current_user]["last_location"] = dict(st.session_state.user_location)
                    save_users(users_db)
                    st.rerun()

            st.markdown(f'<div class="user-location-box"><b>🟢 YOUR POSITION</b><br/>Lat: {user_lat:.4f} | Lng: {user_lng:.4f}</div>', unsafe_allow_html=True)
            st.divider()

            if st.button("🚨 REPORT AT CURRENT LOCATION", use_container_width=True):
                st.session_state.selected_location = dict(st.session_state.user_location)
                st.session_state.confirmation_pending = True
                st.rerun()

        with col_left:
            st.write("📋 **DISPATCH CONSOLE**")
            c_type = st.selectbox("Crime Type", ["Robbery","Grand Theft Auto","Drug Deal","Vandalism","Smuggling"], key="crime_type")
            c_name = st.text_input("Incident Location Name", placeholder="e.g., Downtown Plaza")

            st.divider()

            if st.session_state.confirmation_pending and st.session_state.selected_location:
                loc = st.session_state.selected_location
                st.markdown('<div class="confirmation-box">', unsafe_allow_html=True)
                st.markdown("### ✅ CONFIRM REPORT")
                st.markdown(f"**Lat:** {loc['lat']:.4f} | **Lng:** {loc['lng']:.4f}")
                st.markdown(f"**Type:** {c_type}")
                cc1, cc2 = st.columns(2)
                with cc1:
                    if st.button("✅ YES, CONFIRM", use_container_width=True):
                        loc_name = c_name if c_name else f"{loc['lat']:.4f},{loc['lng']:.4f}"
                        new_incident = {
                            "id":         f"INC-{''.join(random.choices(string.ascii_uppercase+string.digits,k=6))}",
                            "name":       loc_name,
                            "lat":        loc['lat'],
                            "lng":        loc['lng'],
                            "type":       c_type,
                            "reported_by": current_user,
                            "reported_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "votes":      {},          # {username: {vote:"real"/"fake", trust_at_vote:int}}
                            "status":     "open"
                        }
                        incidents.append(new_incident)
                        save_incidents(incidents)
                        st.session_state.selected_location    = None
                        st.session_state.confirmation_pending = False
                        st.balloons()
                        st.success("✅ Incident reported!")
                        st.rerun()
                with cc2:
                    if st.button("❌ NO, RESET", use_container_width=True):
                        st.session_state.selected_location    = None
                        st.session_state.confirmation_pending = False
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.info("Move to location, then click REPORT.")

            st.divider()
            if st.button("🧹 CLEAR ALL INCIDENTS", use_container_width=True):
                incidents.clear()
                save_incidents(incidents)
                st.rerun()

            st.markdown("**📍 ACTIVE INCIDENTS:**")
            if incidents:
                for idx, inc in enumerate(incidents, 1):
                    truth = get_truth_index(inc)
                    color = {"Robbery":"🔴","Grand Theft Auto":"🟠","Drug Deal":"🟣","Vandalism":"🟡","Smuggling":"🔵"}.get(inc['type'],"⚪")
                    dist  = haversine_km(inc['lat'], inc['lng'], user_lat, user_lng)
                    st.caption(f"{color} {idx}. {inc['name']} — {inc['type']} | Truth: {truth}% | {dist:.1f}km")
            else:
                st.caption("No active incidents")

    # ══════════════════════════════════════════
    # PAGE: INCIDENTS (VERIFY)
    # ══════════════════════════════════════════
    elif page == "Incidents":
        st.markdown("<h1>🔍 INCIDENT VERIFICATION</h1>", unsafe_allow_html=True)

        VERIFY_RADIUS_KM = 2.0
        user_lat = st.session_state.user_location['lat']
        user_lng = st.session_state.user_location['lng']

        st.markdown("""
        <div style="background:rgba(0,255,136,0.08);border:1px solid #00ff88;border-radius:10px;padding:15px;margin-bottom:20px;">
        <b style="color:#00ff88;">HOW VERIFICATION WORKS</b><br/>
        You can verify incidents within <b>2km</b> of your current location.<br/>
        Vote <b>REAL</b> or <b>FAKE</b>. Votes are weighted by your Trust Factor.<br/>
        If the community consensus matches your vote → your Trust rises.<br/>
        If it doesn't → your Trust drops. Stay accurate to stay credible!
        </div>
        """, unsafe_allow_html=True)

        # Reload fresh data
        incidents = load_incidents()
        users_db  = load_users()
        user_data = users_db[current_user]

        nearby_incidents = [
            inc for inc in incidents
            if haversine_km(inc['lat'], inc['lng'], user_lat, user_lng) <= VERIFY_RADIUS_KM
        ]
        far_incidents = [
            inc for inc in incidents
            if haversine_km(inc['lat'], inc['lng'], user_lat, user_lng) > VERIFY_RADIUS_KM
        ]

        tf = user_data.get("trust_factor", 50)
        tl, tc = get_trust_label(tf)
        st.markdown(f"**Your Trust Factor:** <span style='color:{tc};font-weight:bold'>{tl} ({tf}/100)</span>", unsafe_allow_html=True)
        st.markdown(f"**Your Location:** {user_lat:.4f}, {user_lng:.4f} | **Verifiable Incidents Nearby:** {len(nearby_incidents)}")
        st.divider()

        # ── Nearby (can verify) ───────────────
        if nearby_incidents:
            st.markdown("### 📡 INCIDENTS IN YOUR AREA (within 2km)")
            for inc in nearby_incidents:
                truth      = get_truth_index(inc)
                votes      = inc.get("votes", {})
                vote_count = len(votes)
                real_count = sum(1 for v in votes.values() if v["vote"] == "real")
                fake_count = vote_count - real_count
                already_voted = current_user in votes
                reported_by = inc.get("reported_by","Unknown")
                rep_trust   = users_db.get(reported_by, {}).get("trust_factor", 50)
                rep_label, rep_color = get_trust_label(rep_trust)
                dist = haversine_km(inc['lat'], inc['lng'], user_lat, user_lng)

                if truth >= 70:   truth_color = "#00ff88"
                elif truth >= 40: truth_color = "#ffcc00"
                else:             truth_color = "#ff4444"

                with st.container(border=True):
                    col_info, col_vote = st.columns([3, 2])
                    with col_info:
                        st.markdown(f"**{inc['name']}** — {inc['type']}")
                        st.markdown(f"📍 {dist:.2f}km away | Reported: {inc.get('reported_at','?')}")
                        st.markdown(f"ID: `{inc['id']}`")
                        st.markdown(
                            f"Reporter: **{reported_by}** "
                            f"<span style='color:{rep_color};font-size:12px;'>({rep_label}, Trust {rep_trust}/100)</span>",
                            unsafe_allow_html=True
                        )
                        st.markdown(
                            f"Truth Index: <span style='color:{truth_color};font-size:18px;font-weight:bold;'>{truth}%</span> "
                            f"| ✅ {real_count} REAL  ❌ {fake_count} FAKE  (Total: {vote_count})",
                            unsafe_allow_html=True
                        )
                        st.progress(truth / 100)

                    with col_vote:
                        if already_voted:
                            my_vote = votes[current_user]["vote"].upper()
                            st.success(f"✔️ You voted: **{my_vote}**")
                        elif inc.get("reported_by") == current_user:
                            st.info("📝 You reported this incident")
                        else:
                            v_col1, v_col2 = st.columns(2)
                            if v_col1.button("✅ REAL", key=f"real_{inc['id']}"):
                                inc["votes"][current_user] = {"vote": "real", "trust_at_vote": tf}
                                user_data["verifications"] = user_data.get("verifications", 0) + 1
                                save_incidents(incidents)
                                # Adjust trust after a short delay (next vote resolution)
                                save_users(users_db)
                                st.rerun()
                            if v_col2.button("❌ FAKE", key=f"fake_{inc['id']}"):
                                inc["votes"][current_user] = {"vote": "fake", "trust_at_vote": tf}
                                user_data["verifications"] = user_data.get("verifications", 0) + 1
                                save_incidents(incidents)
                                save_users(users_db)
                                st.rerun()
        else:
            st.info("📍 No incidents within 2km of your current location. Move closer on the Map page.")

        # ── Trust score resolution ────────────
        # After voting, check closed incidents (5+ votes) and update trust
        changed = False
        users_db = load_users()  # reload fresh before modifying trust
        for inc in incidents:
            if inc.get("status") == "resolved":
                continue
            votes = inc.get("votes", {})
            if len(votes) >= 3:  # resolve after 3 votes
                truth = get_truth_index(inc)
                consensus = "real" if truth >= 50 else "fake"
                for voter, vdata in votes.items():
                    if voter not in users_db:
                        continue
                    if vdata.get("trust_resolved"):
                        continue
                    u = users_db[voter]
                    if vdata["vote"] == consensus:
                        u["trust_factor"] = min(u.get("trust_factor", 50) + 5, 100)
                        u["correct_verifications"] = u.get("correct_verifications", 0) + 1
                    else:
                        u["trust_factor"] = max(u.get("trust_factor", 50) - 7, 0)
                    vdata["trust_resolved"] = True
                    changed = True
                inc["status"] = "resolved"

        if changed:
            save_incidents(incidents)
            save_users(users_db)
            user_data = users_db.get(current_user, user_data)

        st.divider()

        # ── Far incidents (read-only) ─────────
        if far_incidents:
            with st.expander(f"📋 All Other Incidents ({len(far_incidents)} beyond 2km — read-only)"):
                for inc in far_incidents:
                    truth = get_truth_index(inc)
                    votes = inc.get("votes", {})
                    real_c = sum(1 for v in votes.values() if v["vote"]=="real")
                    fake_c = len(votes) - real_c
                    reported_by = inc.get("reported_by","Unknown")
                    rep_trust   = users_db.get(reported_by, {}).get("trust_factor", 50)
                    rep_label, rep_color = get_trust_label(rep_trust)
                    dist = haversine_km(inc['lat'], inc['lng'], user_lat, user_lng)
                    if truth >= 70:   tc2 = "#00ff88"
                    elif truth >= 40: tc2 = "#ffcc00"
                    else:             tc2 = "#ff4444"
                    st.markdown(
                        f"**{inc['name']}** ({inc['type']}) | {dist:.1f}km away | "
                        f"Truth: <span style='color:{tc2}'>{truth}%</span> | "
                        f"✅{real_c} ❌{fake_c} | "
                        f"Reporter: {reported_by} <span style='color:{rep_color};font-size:11px;'>({rep_label})</span>",
                        unsafe_allow_html=True
                    )

        # ── Leaderboard ───────────────────────
        st.divider()
        st.markdown("### 🏆 TRUST LEADERBOARD")
        sorted_users = sorted(users_db.items(), key=lambda x: x[1].get("trust_factor", 50), reverse=True)
        for rank_i, (uname, uinfo) in enumerate(sorted_users[:10], 1):
            tf_i = uinfo.get("trust_factor", 50)
            tl_i, tc_i = get_trust_label(tf_i)
            st.markdown(
                f"**#{rank_i} {uname}** — <span style='color:{tc_i}'>{tl_i} ({tf_i}/100)</span> "
                f"| Verifications: {uinfo.get('verifications',0)}",
                unsafe_allow_html=True
            )

    # ── Always persist user_data changes (merge to avoid overwriting trust updates) ──
    fresh_db = load_users()
    if current_user in fresh_db:
        user_data['trust_factor'] = fresh_db[current_user].get('trust_factor', user_data.get('trust_factor', 50))
        user_data['correct_verifications'] = fresh_db[current_user].get('correct_verifications', user_data.get('correct_verifications', 0))
    fresh_db[current_user] = user_data
    save_users(fresh_db)