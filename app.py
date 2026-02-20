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
    # Generates a unique "Gangster ID" like VC-X89L2
    return "VC-" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

# --- CSS STYLING (Black Background & Neon Accents) ---
st.markdown("""
<style>
/* Force Black Background for the entire app */
.stApp {
    background-color: #000000;
}
html, body, [class*="css"] {
    background-color: #000000;
    color: white;
}
h1 {
    color: #ff00aa;
    text-align: center;
    font-size: 60px;
    text-shadow: 0 0 10px #ff00aa, 0 0 20px #00ffff;
}
h3 {
    color: #00ffff;
}
/* Neon Buttons */
div.stButton > button {
    background-color: black;
    color: #00ffff;
    border: 2px solid #ff00aa;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
    transition: 0.3s;
}
div.stButton > button:hover {
    border-color: #00ffff;
    color: #ff00aa;
    box-shadow: 0 0 15px #ff00aa;
}
/* Profile Card Styling */
.profile-card {
    border: 1px solid #ff00aa;
    padding: 15px;
    border-radius: 10px;
    background: rgba(255, 0, 170, 0.05);
}
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None

# Load the permanent database
users_db = load_users()

# --- SCREEN 1: THE LOGIN/SIGNUP GATE ---
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        # Toggle between Login and Signup
        mode = st.radio("SELECT PROTOCOL", ["LOGIN", "CREATE ACCOUNT"], horizontal=True)
        st.divider()

        if mode == "LOGIN":
            user_input = st.text_input("OPERATOR ID")
            pw_input = st.text_input("SECURITY CIPHER", type="password")
            
            if st.button("INITIALIZE SESSION"):
                if user_input in users_db and users_db[user_input]["password"] == pw_input:
                    st.session_state.logged_in = True
                    st.session_state.current_user = user_input
                    st.rerun()
                else:
                    st.error("ACCESS DENIED: Credentials Invalid")
        
        else:
            st.markdown("<small style='color:#00ffff;'>Enter details to generate your unique city code.</small>", unsafe_allow_html=True)
            new_user = st.text_input("CHOOSE OPERATOR NAME")
            new_pw = st.text_input("SET CIPHER", type="password")
            
            if st.button("GENERATE ID & REGISTER"):
                if new_user in users_db:
                    st.warning("Operator ID already taken.")
                elif new_user and new_pw:
                    code = generate_account_code()
                    users_db[new_user] = {
                        "password": new_pw,
                        "respect": 50,
                        "code": code
                    }
                    save_users(users_db)
                    st.success(f"WELCOME TO THE FAMILY! Your Unique ID is: {code}")
                    st.info("You can now switch to LOGIN to enter.")
                else:
                    st.error("The Boss requires a name and a cipher.")

# --- SCREEN 2: THE MAIN REPUTATION ENGINE ---
else:
    # Get current user data from the DB
    user_data = users_db[st.session_state.current_user]
    
    # Sidebar: Profile & Missions
    st.sidebar.markdown(f"## 👤 {st.session_state.current_user}")
    
    # Profile Access (Expander acts as a pop-up profile)
    with st.sidebar.expander("📂 VIEW OPERATOR PROFILE"):
        st.markdown(f"""
        <div class="profile-card">
        <p style="color:#00ffff; margin-bottom:5px;"><b>ID CODE:</b> {user_data['code']}</p>
        <p style="color:#ff00aa; margin-bottom:5px;"><b>RANK:</b> Street Associate</p>
        <p style="color:white; margin-bottom:5px;"><b>CURRENT RESPECT:</b> {user_data['respect']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.sidebar.divider()
    
    st.sidebar.header("🎯 MISSIONS")
    if st.sidebar.button("Secure Perimeter (+10 Respect)"):
        users_db[st.session_state.current_user]["respect"] = min(user_data["respect"] + 10, 100)
        save_users(users_db)
        st.rerun()
    
    if st.sidebar.button("Spread Misinformation (-20 Respect)"):
        users_db[st.session_state.current_user]["respect"] = max(user_data["respect"] - 20, 0)
        save_users(users_db)
        st.rerun()

    if st.sidebar.button("LOGOUT"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()

    # Main Dashboard
    try:
        st.image("Grand20Coders.png", use_column_width=True)
    except:
        st.info("Header image not found.")

    st.markdown(f"<h1>🌴 Reputation Engine</h1>", unsafe_allow_html=True)
    
    # Respect Display
    st.markdown(f"<h3>Status: {st.session_state.current_user}</h3>", unsafe_allow_html=True)
    st.progress(user_data["respect"] / 100)
    st.write(f"Respect Points: {user_data['respect']}")

    # Logic-based Access Levels
    if user_data["respect"] >= 80:
        st.success("ACCESS LEVEL: GOLD ZONE")
    elif user_data["respect"] >= 50:
        st.warning("ACCESS LEVEL: SILVER ZONE")
    else:
        st.error("ACCESS LEVEL: RESTRICTED")