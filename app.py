import streamlit as st
import random
import string
import json
import os

# --- DATABASE LOGIC ---
DB_FILE = "users.json"

def load_data():
    """Loads the user database from a JSON file."""
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return {} # Return empty dict if file doesn't exist yet

def save_data(data):
    """Saves the current user database to the JSON file."""
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Replace 'st.session_state.user_db = {}' with this:
if "user_db" not in st.session_state:
    st.session_state.user_db = load_data()
# 1. Page Configuration
st.set_page_config(page_title="Vice City | The Gate", layout="wide")

# 2. 🔥 Custom Neon CSS with BLURRED BACKGROUND
# Replace 'Grand Theft Coders.png' with your actual filename
bg_img = "Grand Theft Coders.png" 

st.markdown(f"""
<style>
/* Background Image with Blur Effect */
.stApp {{
    background-image: url("https://images.unsplash.com/photo-1614850523296-d8c1af93d400?ixlib=rb-4.0.3&auto=format&fit=crop&w=2070&q=80"); /* Placeholder if local fails */
    background-size: cover;
    background-attachment: fixed;
}}

/* The Magic Blur Overlay */
.stApp::before {{
    content: "";
    position: absolute;
    top: 0; left: 0; width: 100%; height: 100%;
    background: rgba(0, 0, 0, 0.7); /* Darkens the image */
    backdrop-filter: blur(8px); /* This creates the blur */
    z-index: -1;
}}

/* Login Box Styling */
.login-container {{
    background-color: rgba(20, 20, 20, 0.8);
    padding: 30px;
    border-radius: 15px;
    border: 2px solid #ff00aa;
    box-shadow: 0 0 20px #ff00aa;
    max-width: 400px;
    margin: auto;
}}

h1 {{
    color: #ff00aa;
    text-shadow: 0 0 10px #ff00aa;
    text-align: center;
}}
</style>
""", unsafe_allow_html=True)

# 3. Database Simulation (We'll use Session State)
if "user_db" not in st.session_state:
    st.session_state.user_db = {} # Format: {username: {"password": pwd, "code": code, "respect": 50}}

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# 4. Helper Functions
def generate_account_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# 5. Auth Logic
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 VICE CITY GATEKEEPER</h1>", unsafe_allow_html=True)
    
    tab1, tab2 = st.tabs(["🔑 Login", "📝 Create Account"])
    
    with tab1:
        user_input = st.text_input("Username", key="login_user")
        pass_input = st.text_input("Password", type="password", key="login_pass")
        if st.button("Enter the City"):
            if user_input in st.session_state.user_db and st.session_state.user_db[user_input]["password"] == pass_input:
                st.session_state.logged_in = True
                st.session_state.current_user = user_input
                st.rerun()
            else:
                st.error("Invalid credentials, rookie.")

    with tab2:
        new_user = st.text_input("Choose Username", key="reg_user")
        new_pass = st.text_input("Choose Password", type="password", key="reg_pass")
        
        if st.button("Generate My ID & Join"):
            if new_user and new_pass:
                if new_user not in st.session_state.user_db:
                    account_code = generate_account_code()
                    st.session_state.user_db[new_user] = {
                        "password": new_pass,
                        "code": account_code,
                        "respect": 50
                    }
                    st.success(f"Welcome to the family! Your unique ID is: **{account_code}**")
                    st.info("You can now login on the first tab.")
                else:
                    st.warning("Username already taken.")
            else:
                st.error("Fill in the blanks!")

else:
    # --- LOGGED IN CONTENT (Your Reputation Engine) ---
    user_data = st.session_state.user_db[st.session_state.current_user]
    
    st.sidebar.write(f"👤 **User:** {st.session_state.current_user}")
    st.sidebar.write(f"🆔 **ID:** {user_data['code']}")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # (Insert your Reputation Engine code here)
    st.markdown(f"<h1>Welcome back, {st.session_state.current_user}</h1>", unsafe_allow_html=True)
    st.write(f"Your respect level is currently: {user_data['respect']}")