import streamlit as st
import random

# 1. Page Configuration
st.set_page_config(page_title="Vice City Reputation Engine", layout="wide")

# 2. 🔥 Custom Neon CSS
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #000000;
    color: white;
}
.block-container {
    padding-top: 1rem;
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
div.stButton > button {
    background-color: black;
    color: #00ffff;
    border: 2px solid #ff00aa;
    border-radius: 10px;
    font-weight: bold;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# --- SESSION INITIALIZATION ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "respect" not in st.session_state:
    st.session_state.respect = 50

# --- SCREEN 1: THE LOGIN GATE ---
if not st.session_state.logged_in:
    st.markdown("<h1>🌴 VICE CITY GATEWAY</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        user = st.text_input("Operator ID")
        pw = st.text_input("Security Cipher", type="password")
        
        if st.button("INITIALIZE SESSION"):
            if user == "admin" and pw == "vice84":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("ACCESS DENIED")

# --- SCREEN 2: THE MAIN CONTENT ---
else:
    # We use a try/except block here so the app doesn't crash if the image is missing
    try:
        st.image("Grand20Coders.png", use_container_width=True)
    except:
        st.warning("⚠️ Image 'Grand Theft Coders.png' not found in repository.")

    st.markdown("<h1>🌴 Vice City Reputation Engine</h1>", unsafe_allow_html=True)
    
    # Sidebar Missions
    st.sidebar.header("🎯 Missions")
    if st.sidebar.button("Secure Perimeter (+10 Respect)"):
        st.session_state.respect = min(st.session_state.respect + 10, 100)
    
    if st.sidebar.button("Spread Misinformation (-20 Respect)"):
        st.session_state.respect = max(st.session_state.respect - 20, 0)

    # UI Display
    st.markdown(f"<h3>Current Respect: {st.session_state.respect}</h3>", unsafe_allow_html=True)
    st.progress(st.session_state.respect / 100)