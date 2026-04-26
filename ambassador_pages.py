import json
from html import escape

import streamlit as st

from github_analyzer import analyze_github, render_github_analysis
from helpers import (
    get_ambassador_tasks,
    get_ambassadors_with_github,
    get_org,
    get_user,
    get_user_badges,
    save_github_data,
    submit_task,
)
from ui_components import TYPE_COLORS, app_sidebar, avatar, badge_progress, metric_card, next_priority, score_pill, section_label, tag, fetch_badge_catalog


def leaderboard_page(org_id, title_text):
    ambassadors = get_ambassadors_with_github(org_id)
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Leaderboard</div>
            <div class="hero-title">{escape(title_text)}</div>
            <div class="hero-subtitle">Points reward execution. GitHub scoring adds an extra layer of public signal.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if not ambassadors:
        st.markdown('<div class="empty">No leaderboard data yet.</div>', unsafe_allow_html=True)
        return

    ranked = sorted(ambassadors, key=lambda item: (item.get("points", 0), item.get("github_score") or 0), reverse=True)
    for index, ambassador in enumerate(ranked, start=1):
        accent = "#6ea8fe" if index == 1 else "#34d3b4" if index == 2 else "#9b8cff" if index == 3 else "#29324b"
        badges = get_user_badges(ambassador["id"])
        badge_line = " ".join(badge["icon"] for badge in badges[:5]) or "-"
        gh_score = ambassador.get("github_score") or 0
        st.markdown(
            f"""
            <div class="leader-card" style="border-color:{accent}55;">
                <div style="display:flex;align-items:center;gap:14px;">
                    <div style="font-family:'Manrope',sans-serif;font-size:1.4rem;font-weight:800;width:42px;">#{index}</div>
                    {avatar(ambassador["name"], ambassador.get("avatar_color", accent), 46)}
                    <div style="flex:1;">
                        <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:800;">{escape(ambassador['name'])}</div>
                        <div style="color:#8c98b8;font-size:0.82rem;">{escape(ambassador.get('college') or 'College not added')} - {escape(badge_line)}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Manrope',sans-serif;font-size:1.25rem;font-weight:800;">{ambassador['points']} pts</div>
                        <div style="margin-top:6px;">{score_pill(gh_score, 'GitHub') if ambassador.get('github_username') else '<span class="pill">No GitHub</span>'}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def ambassador_home(user, org):
    from helpers import get_ambassador_stats

    stats = get_ambassador_stats(user["id"], org["id"])
    tasks = get_ambassador_tasks(user["id"], org["id"])
    badges = get_user_badges(user["id"])
    priority = next_priority(tasks)
    rank_list = get_ambassadors_with_github(org["id"])
    rank = next((index for index, ambassador in enumerate(rank_list, start=1) if ambassador["id"] == user["id"]), None)
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Ambassador dashboard</div>
            <div class="hero-title">Your signal inside {escape(org['name'])}</div>
            <div class="hero-subtitle">Keep your execution streak alive and strengthen your public proof with GitHub.</div>
            <div class="hero-note">You are currently ranked #{rank or '-'} with {stats['points']} points and {stats['pending']} submissions in review.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cols[0].markdown(metric_card(stats["points"], "Points", "Program score"), unsafe_allow_html=True)
    cols[1].markdown(metric_card(stats["tasks_done"], "Completed", "Approved tasks"), unsafe_allow_html=True)
    cols[2].markdown(metric_card(stats["pending"], "In review", "Awaiting decision"), unsafe_allow_html=True)
    cols[3].markdown(metric_card(user.get("github_score") or 0, "GitHub score", user.get("github_tier") or "Not linked"), unsafe_allow_html=True)

    gap_to_next_badge = badge_progress(user, org["id"])
    next_badge_text = (
        f"Closest badge: {gap_to_next_badge[0]['name']} at {gap_to_next_badge[0]['current']}/{gap_to_next_badge[0]['target']}."
        if gap_to_next_badge
        else "All available badges are unlocked."
    )
    github_cta = (
        f"Your public GitHub signal is {user.get('github_score') or 0}/100."
        if user.get("github_username")
        else "Link GitHub to add public proof beyond task execution."
    )
    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="insight-card">
                <div class="title">Momentum</div>
                <div class="text">{escape(next_badge_text)}</div>
            </div>
            <div class="insight-card">
                <div class="title">Signal check</div>
                <div class="text">{escape(github_cta)}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.1, 0.9], gap="large")
    with left:
        section_label("Next best move")
        if priority:
            st.markdown(
                f"""
                <div class="task-card">
                    {tag(priority["task_type"].title(), TYPE_COLORS.get(priority["task_type"], "#9b8cff"))}
                    <div style="font-family:'Manrope',sans-serif;font-size:1.12rem;font-weight:800;margin-top:10px;">{escape(priority['title'])}</div>
                    <div style="color:#8c98b8;margin-top:6px;">{escape(priority['description'] or 'No description added.')}</div>
                    <div style="margin-top:12px;" class="pill">{priority['points_reward']} points available</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown('<div class="empty">You have already submitted every open task.</div>', unsafe_allow_html=True)

        section_label("Badge progress")
        progress = badge_progress(user, org["id"])
        if progress:
            for item in progress:
                st.markdown(
                    f"""
                    <div class="panel-card">
                        <div style="display:flex;justify-content:space-between;gap:12px;">
                            <div style="font-family:'Manrope',sans-serif;font-weight:800;">{escape(item['icon'])} {escape(item['name'])}</div>
                            <div style="color:#8c98b8;font-size:0.84rem;">{item['current']}/{item['target']}</div>
                        </div>
                        <div style="color:#8c98b8;font-size:0.84rem;margin-top:4px;">{escape(item['description'])}</div>
                        <div style="margin-top:12px;" class="bar-track"><div class="bar-fill" style="width:{item['pct']}%;"></div></div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty">You have earned every badge currently available.</div>', unsafe_allow_html=True)

    with right:
        section_label("Your profile")
        gh_score = user.get("github_score") or 0
        gh_name = user.get("github_username")
        cards = [
            (
                "GitHub positioning",
                "@" + gh_name if gh_name else "No GitHub linked yet",
                score_pill(gh_score, "GitHub") if gh_name else '<span class="pill">Add GitHub to stand out</span>',
            ),
            ("Badges earned", f"{len(badges)} badges unlocked so far.", ""),
            (
                "How to improve fast",
                "Submit higher-value tasks, keep your streak active, and analyze your GitHub profile to make your public work easier to evaluate.",
                "",
            ),
        ]
        for title, body, extra in cards:
            st.markdown(
                f"""
                <div class="soft-card">
                    <div style="font-family:'Manrope',sans-serif;font-weight:800;">{escape(title)}</div>
                    <div style="color:#8c98b8;margin-top:6px;">{escape(body)}</div>
                    {f'<div style="margin-top:10px;">{extra}</div>' if extra else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )


def ambassador_tasks_page(user, org):
    tasks = get_ambassador_tasks(user["id"], org["id"])
    available = [task for task in tasks if not task["sub_id"]]
    submitted = [task for task in tasks if task["sub_id"]]
    available_tab, submitted_tab = st.tabs(["Available tasks", "Submitted work"])

    with available_tab:
        if not available:
            st.markdown('<div class="empty">No open tasks are waiting for you right now.</div>', unsafe_allow_html=True)
        for task in sorted(available, key=lambda item: item["points_reward"], reverse=True):
            with st.expander(f"{task['title']} - {task['points_reward']} pts"):
                st.markdown(f"**Type**: {task['task_type'].title()}")
                st.markdown(f"**Deadline**: {task['deadline'] or 'Open'}")
                st.markdown(f"**Brief**: {task['description'] or 'No description added.'}")
                with st.form(f"submit_{task['id']}"):
                    proof_text = st.text_area("What did you do?", height=110)
                    proof_link = st.text_input("Proof link")
                    if st.form_submit_button("Submit for review", use_container_width=True):
                        ok, msg = submit_task(task["id"], user["id"], proof_text, proof_link)
                        st.success(msg) if ok else st.error(msg)
                        st.rerun()

    with submitted_tab:
        if not submitted:
            st.markdown('<div class="empty">You have not submitted any tasks yet.</div>', unsafe_allow_html=True)
        for task in submitted:
            color = {"approved": "#34d3b4", "pending": "#ffb86b", "rejected": "#ff6b81"}.get(task["sub_status"], "#8c98b8")
            st.markdown(
                f"""
                <div class="task-card">
                    <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                        <div>
                            {tag(task["task_type"].title(), TYPE_COLORS.get(task["task_type"], "#9b8cff"))}
                            <div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:800;margin-top:8px;">{escape(task['title'])}</div>
                            <div style="color:#8c98b8;font-size:0.84rem;margin-top:6px;">Status: <span style="color:{color};font-weight:700;">{escape(task['sub_status'].title())}</span></div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:'Manrope',sans-serif;font-size:1.15rem;font-weight:800;">{task['sub_score'] or 0} pts</div>
                        </div>
                    </div>
                    {f'<div style="color:#8c98b8;font-size:0.84rem;margin-top:10px;">Feedback: {escape(task["feedback"])}</div>' if task.get("feedback") else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )


def ambassador_github_page(user):
    current = user.get("github_username") or ""
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Personal GitHub signal</div>
            <div class="hero-title">Turn your public work into a stronger application story</div>
            <div class="hero-subtitle">Analyze your GitHub once, save the score, and make your technical profile easier for organizations to trust.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    with st.form("amb_github_form"):
        username = st.text_input("GitHub username", value=current, placeholder="for example: torvalds")
        token = st.text_input("Token", type="password", placeholder="Optional, improves rate limits")
        if st.form_submit_button("Analyze and save", use_container_width=True):
            if username.strip():
                with st.spinner(f"Analyzing @{username.strip()}"):
                    data = analyze_github(username, token or None)
                if data.get("found"):
                    save_github_data(user["id"], username.strip(), data["overall_score"], data["tier"], json.dumps(data))
                    st.session_state.user["github_username"] = username.strip()
                    st.session_state.user["github_score"] = data["overall_score"]
                    st.session_state.user["github_tier"] = data["tier"]
                    st.session_state.gh_cache[username.strip().lower()] = data
                    st.success("GitHub profile saved.")
                render_github_analysis(data)

    key = (st.session_state.user.get("github_username") or "").lower()
    st.markdown(
        """
        <div class="insight-grid">
            <div class="insight-card">
                <div class="title">What improves the score</div>
                <div class="text">Recent pushes, original projects, a complete profile, and visible repository traction all help your public signal.</div>
            </div>
            <div class="insight-card">
                <div class="title">Best use in a demo</div>
                <div class="text">Show the before and after: link your username, run the analysis, then compare how your profile looks to an evaluator.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if key and key in st.session_state.gh_cache:
        render_github_analysis(st.session_state.gh_cache[key])


def ambassador_badges_page(user):
    earned = get_user_badges(user["id"])
    earned_ids = {badge["id"] for badge in earned}
    all_badges = fetch_badge_catalog()
    section_label("Earned badges")
    if earned:
        cols = st.columns(3)
        for index, badge in enumerate(earned):
            cols[index % 3].markdown(
                f"""
                <div class="panel-card" style="text-align:center;">
                    <div style="font-size:2rem;">{escape(badge['icon'])}</div>
                    <div style="font-family:'Manrope',sans-serif;font-weight:800;margin-top:8px;">{escape(badge['name'])}</div>
                    <div style="color:#8c98b8;font-size:0.84rem;margin-top:5px;">{escape(badge['description'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown('<div class="empty">No badges yet. Complete tasks to start unlocking them.</div>', unsafe_allow_html=True)

    section_label("Still locked")
    locked = [badge for badge in all_badges if badge["id"] not in earned_ids]
    if locked:
        cols = st.columns(3)
        for index, badge in enumerate(locked):
            cols[index % 3].markdown(
                f"""
                <div class="panel-card" style="text-align:center;opacity:0.7;">
                    <div style="font-size:2rem;">{escape(badge['icon'])}</div>
                    <div style="font-family:'Manrope',sans-serif;font-weight:800;margin-top:8px;">{escape(badge['name'])}</div>
                    <div style="color:#8c98b8;font-size:0.84rem;margin-top:5px;">{escape(badge['description'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_ambassador_app(user):
    fresh_user = get_user(user["id"]) or user
    st.session_state.user = fresh_user
    org = get_org(fresh_user["org_id"])
    page = app_sidebar(
        fresh_user,
        org,
        {
            "Dashboard": "dashboard",
            "Tasks": "tasks",
            "My GitHub": "github",
            "Badges": "badges",
            "Leaderboard": "leaderboard",
        },
        fresh_user.get("college") or "Ambassador",
    )
    if page == "dashboard":
        ambassador_home(fresh_user, org)
    elif page == "tasks":
        ambassador_tasks_page(fresh_user, org)
    elif page == "github":
        ambassador_github_page(fresh_user)
    elif page == "badges":
        ambassador_badges_page(fresh_user)
    else:
        leaderboard_page(org["id"], "How you compare across the ambassador program")
