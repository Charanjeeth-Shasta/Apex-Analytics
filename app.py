import streamlit as st

st.set_page_config(
    page_title="Apex Analytics",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

home_page = st.Page("views/landing.py",  title="Home",           icon="🏠", default=True)
auth_page = st.Page("views/auth.py",     title="Login / Signup", icon="🔐")
dash_page = st.Page("views/dashboard.py",title="Dashboard",      icon="📊")

pg = st.navigation([home_page, auth_page, dash_page])
pg.run()
