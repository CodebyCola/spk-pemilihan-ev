import streamlit as st

dashboard_page = st.Page("dashboard.py", title="Dashboard")
process_page = st.Page("process.py", title="Process")
profile_page = st.Page("profile.py", title="Profile")

st.set_page_config(page_title="SCPK")
pg = st.navigation({"Tools": [dashboard_page, process_page, profile_page]})
pg.run()

