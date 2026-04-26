import streamlit as st

from ambassador_pages import render_ambassador_app
from auth_page import show_auth
from database import init_db
from org_pages import render_org_app
from ui_theme import inject_styles


st.set_page_config(page_title="CampusConnect", page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
init_db()

if "user" not in st.session_state:
    st.session_state.user = None
if "gh_cache" not in st.session_state:
    st.session_state.gh_cache = {}
if "review_profile" not in st.session_state:
    st.session_state.review_profile = None

inject_styles()

if not st.session_state.user:
    show_auth()
elif st.session_state.user["role"] == "org":
    render_org_app(st.session_state.user)
else:
    render_ambassador_app(st.session_state.user)
