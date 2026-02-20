import streamlit as st
import random

st.set_page_config(page_title="Vice City Reputation Engine", layout="wide")

st.title("🌴 Vice City Reputation Engine")
st.markdown("### Turn Panic into Points.")

# Initialize session state
if "respect" not in st.session_state:
    st.session_state.respect = 50

# Sidebar Missions
st.sidebar.header("🎯 Missions")

if st.sidebar.button("Stay Indoors During Storm (+10 Respect)"):
    st.session_state.respect += 10

if st.sidebar.button("Spread Misinformation (-20 Respect)"):
    st.session_state.respect -= 20

# Display Respect Score
st.subheader("🏆 Respect Score")
st.progress(st.session_state.respect)

# Access Logic
if st.session_state.respect >= 80:
    st.success("Access Level: GOLD ZONE")
elif st.session_state.respect >= 50:
    st.warning("Access Level: SILVER ZONE")
else:
    st.error("Access Level: RESTRICTED")

# Fake live data
st.subheader("📡 City Behavior Feed")
st.write({
    "Active Citizens": random.randint(1000, 5000),
    "Heat Level": random.randint(1, 5),
    "Storm Severity": random.randint(1, 10)
})