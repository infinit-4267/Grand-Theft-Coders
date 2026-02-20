import streamlit as st
import random

# 1. Page Configuration
st.set_page_config(page_title="Vice City Reputation Engine", layout="wide")

# 2. HEADER IMAGE 🌴
# Ensure "Grand Theft Coders.png" is in the same folder as this script
st.image("Grand Theft Coders.png", use_container_width=True)

# 3. 🔥 Custom Neon CSS
st.markdown("""
<style>
/* Reset background and text colors */
html, body, [class*="css"]  {
    background-color: #000000;
    color: white;
}
/* Reduce spacing between the image and the title */
.block-container {
    padding-top: 1rem;
}
/* Neon Title Styling */
h1 {
    color: #ff00aa;
    text-align: center;
    font-size: 60px;
    text-shadow: 0 0 10px #ff00aa, 0 0 20px #00ffff;
}
h3 {
    color: #00ffff;
}
/* Progress bar and button styling */
div.stProgress > div > div > div > div {
    background-color: #00ffff;
}
div.stButton > button {
    background-color: black;
    color: #00ffff;
    border: 2px solid #ff00aa;
    border-radius: 10px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# 4. 🏝 Main Content
st.markdown("<h1>🌴 Vice City Reputation Engine</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Turn Panic Into Points</h3>", unsafe_allow_html=True)

# Initialize session state for respect points
if "respect" not in st.session_state:
    st.session_state.respect = 50

# Sidebar for "Missions"
st.sidebar.header("🎯 Missions")
if st.sidebar.button("Secure Perimeter (+10 Respect)"):
    st.session_state.respect += 10
if st.sidebar.button("Spread Misinformation (-20 Respect)"):
    st.session_state.respect -= 20

# Respect Score Display
st.markdown("### 🏆 Respect Score")
st.progress(min(max(st.session_state.respect, 0), 100)) # Clamping value between 0-100
st.markdown(f"<h3>Current Score: {st.session_state.respect}</h3>", unsafe_allow_html=True)

# Access Logic based on score
if st.session_state.respect >= 80:
    st.success("ACCESS LEVEL: GOLD ZONE")
elif st.session_state.respect >= 50:
    st.warning("ACCESS LEVEL: SILVER ZONE")
else:
    st.error("ACCESS LEVEL: RESTRICTED")