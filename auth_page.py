import streamlit as st

from helpers import login_user, register_ambassador, register_org


def show_auth():
    left, right = st.columns([1.2, 0.9], gap="large")
    with left:
        st.markdown(
            """
            <div class="hero-card">
                <div class="eyebrow">Campus ambassador OS</div>
                <div class="hero-title">Fast GitHub assessment for campus programs</div>
                <div class="hero-subtitle">Run your ambassador workflow, review submissions, and understand public technical signals from one dark, focused workspace.</div>
                <div class="mini-grid">
                    <div class="mini-card">
                        <b>Under two minutes</b>
                        One username produces a quick verdict with proof points and signal breakdowns.
                    </div>
                    <div class="mini-card">
                        <b>Better judging story</b>
                        GitHub evaluation sits inside a real ambassador management flow, not beside it.
                    </div>
                    <div class="mini-card">
                        <b>Cleaner workflow</b>
                        Organizations and ambassadors both get sharper dashboards and faster actions.
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="panel-card">
                <div class="eyebrow">Built for demos</div>
                <div style="font-family:'Manrope',sans-serif;font-size:1.22rem;font-weight:800;margin-top:6px;">A shortlist engine for student communities</div>
                <div style="color:#8c98b8;margin-top:8px;">
                    Start with a public GitHub profile, then connect that signal to execution data like tasks, reviews, points, and badges.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            """
            <div class="panel-card" style="padding-bottom:10px;">
                <div class="eyebrow">Welcome back</div>
                <div style="font-family:'Manrope',sans-serif;font-size:1.8rem;font-weight:800;margin-top:6px;">Sign in or launch a program</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        login_tab, org_tab, amb_tab = st.tabs(["Login", "Create organization", "Join as ambassador"])

        with login_tab:
            with st.form("login_form"):
                email = st.text_input("Email", placeholder="org@demo.com or arjun@demo.com")
                password = st.text_input("Password", type="password", placeholder="demo123")
                if st.form_submit_button("Log in", use_container_width=True):
                    user = login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.rerun()
                    st.error("Invalid credentials.")
            st.info("Demo password: demo123")

        with org_tab:
            with st.form("org_form"):
                name = st.text_input("Your name")
                email = st.text_input("Work email")
                password = st.text_input("Password", type="password")
                org_name = st.text_input("Organization name")
                org_desc = st.text_area("What does your team do?", height=90)
                if st.form_submit_button("Create organization", use_container_width=True):
                    ok, msg = register_org(name, email, password, org_name, org_desc)
                    st.success(msg) if ok else st.error(msg)

        with amb_tab:
            with st.form("amb_form"):
                name = st.text_input("Your name")
                email = st.text_input("Email")
                password = st.text_input("Password", type="password")
                college = st.text_input("College")
                invite_code = st.text_input("Invite code")
                github_username = st.text_input("GitHub username", placeholder="optional")
                if st.form_submit_button("Join program", use_container_width=True):
                    ok, msg = register_ambassador(name, email, password, college, invite_code, github_username)
                    st.success(msg) if ok else st.error(msg)
