import streamlit as st
import random

st.set_page_config(page_title="Vice City Reputation Engine", layout="wide")

# 🔥 Custom Neon CSS
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #000000;
    color: white;
}

/* Main title */
h1 {
    color: #ff00aa;
    text-align: center;
    font-size: 60px;
    text-shadow: 0 0 10px #ff00aa, 0 0 20px #00ffff;
}

/* Subheaders */
h3 {
    color: #00ffff;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #111111;
}

/* Buttons */
div.stButton > button {
    background-color: black;
    color: #00ffff;
    border: 2px solid #ff00aa;
    border-radius: 10px;
    font-weight: bold;
}
div.stButton > button:hover {
    background-color: #ff00aa;
    color: black;
    box-shadow: 0 0 15px #ff00aa;
}

/* Progress bar */
div.stProgress > div > div > div > div {
    background-color: #00ffff;
}
</style>
""", unsafe_allow_html=True)

# 🏝 Title
st.markdown("<h1>🌴 Vice City Reputation Engine</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Turn Panic Into Points</h3>", unsafe_allow_html=True)

# Initialize session
if "respect" not in st.session_state:
    st.session_state.respect = 50

# Sidebar missions
st.sidebar.header("🎯 Missions")

if st.sidebar.button("Secure Perimeter (+10 Respect)"):
    st.session_state.respect += 10

if st.sidebar.button("Spread Misinformation (-20 Respect)"):
    st.session_state.respect -= 20

# Respect Score Display
st.markdown("### 🏆 Respect Score")
st.progress(st.session_state.respect)

st.markdown(f"<h3>Current Score: {st.session_state.respect}</h3>", unsafe_allow_html=True)

# Access Logic
if st.session_state.respect >= 80:
    st.success("ACCESS LEVEL: GOLD ZONE")
elif st.session_state.respect >= 50:
    st.warning("ACCESS LEVEL: SILVER ZONE")
else:
    st.error("ACCESS LEVEL: RESTRICTED")

# Fake Live Data
st.markdown("### 📡 Live City Feed")
st.write({
    "Active Citizens": random.randint(1000, 5000),
    "Heat Level": random.randint(1, 5),
    "Storm Severity": random.randint(1, 10)
})