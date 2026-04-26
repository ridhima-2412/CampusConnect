import json
from html import escape

import streamlit as st

from github_analyzer import analyze_github, render_github_analysis
from helpers import (
    create_task,
    get_ambassadors_with_github,
    get_org,
    get_org_stats,
    get_pending_submissions,
    get_shortlist_board,
    get_tasks,
    get_user,
    get_user_badges,
    review_submission,
    save_pipeline_status,
)
from ui_components import TYPE_COLORS, app_sidebar, avatar, metric_card, score_pill, score_tone, section_label, tag


PIPELINE_STYLES = {
    "watch": ("Watch", "#ffb86b"),
    "shortlist": ("Shortlist", "#6ea8fe"),
    "high_potential": ("High Potential", "#34d3b4"),
}


def pipeline_pill(status):
    label, tone = PIPELINE_STYLES.get(status or "watch", PIPELINE_STYLES["watch"])
    return (
        f'<span class="pill" style="color:{tone};border-color:{tone}33;background:{tone}12;">'
        f"{label}</span>"
    )


def org_overview(org, user):
    stats = get_org_stats(org["id"])
    ambassadors = get_ambassadors_with_github(org["id"])
    pending = get_pending_submissions(org["id"])
    tasks = get_tasks(org["id"])
    linked = [amb for amb in ambassadors if amb.get("github_username")]
    unlinked_count = len(ambassadors) - len(linked)
    avg_points = int(sum(amb.get("points", 0) for amb in ambassadors) / len(ambassadors)) if ambassadors else 0
    avg_github = int(sum((amb.get("github_score") or 0) for amb in linked) / len(linked)) if linked else 0
    approval_rate = 0
    if stats["approved_submissions"] + stats["pending_review"]:
        approval_rate = int(stats["approved_submissions"] / (stats["approved_submissions"] + stats["pending_review"]) * 100)

    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Command center</div>
            <div class="hero-title">{escape(org["name"])} runs better with proof and signal</div>
            <div class="hero-subtitle">Welcome back, {escape(user["name"].split()[0])}. Keep review speed high and push more ambassadors to link GitHub for stronger comparisons.</div>
            <div class="hero-note">You have {stats['pending_review']} items waiting, {stats.get('github_linked', 0)} GitHub links, and an approval rate of {approval_rate}%.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(5)
    items = [
        (stats["total_ambassadors"], "Ambassadors", "Active roster"),
        (stats["total_tasks"], "Tasks", "Live missions"),
        (stats["approved_submissions"], "Approved", "Completed reviews"),
        (stats["pending_review"], "In review", "Needs action"),
        (stats.get("shortlisted", 0) + stats.get("high_potential", 0), "Pipeline picks", "Watchlist in motion"),
    ]
    for col, item in zip(cols, items):
        col.markdown(metric_card(*item), unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="insight-grid">
            <div class="insight-card">
                <div class="title">Benchmark snapshot</div>
                <div class="text">Average ambassador output is {avg_points} points and the average linked GitHub score is {avg_github}/100.</div>
            </div>
            <div class="insight-card">
                <div class="title">Next leverage move</div>
                <div class="text">The fastest quality gain is reducing the {stats['pending_review']} item review queue and nudging {unlinked_count} ambassadors to connect GitHub.</div>
            </div>
            <div class="insight-card">
                <div class="title">Shortlist board</div>
                <div class="text">{stats.get('shortlisted', 0)} ambassadors are shortlisted and {stats.get('high_potential', 0)} are marked high potential.</div>
            </div>
            <div class="insight-card">
                <div class="title">GitHub adoption</div>
                <div class="text">{stats.get('github_linked', 0)} ambassadors already have a public technical signal connected.</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    left, right = st.columns([1.25, 0.75], gap="large")
    with left:
        section_label("Top ambassadors")
        if ambassadors:
            for index, ambassador in enumerate(ambassadors[:5], start=1):
                gh = ambassador.get("github_score") or 0
                badges = get_user_badges(ambassador["id"])
                badge_line = " ".join(badge["icon"] for badge in badges[:5]) or "No badges yet"
                st.markdown(
                    f"""
                    <div class="leader-card">
                        <div class="profile-row">
                            {avatar(ambassador["name"], ambassador.get("avatar_color", "#6ea8fe"), 44)}
                            <div style="flex:1;">
                                <div style="font-family:'Manrope',sans-serif;font-weight:800;">{index}. {escape(ambassador["name"])}</div>
                                <div style="color:#8c98b8;font-size:0.84rem;">{escape(ambassador.get("college") or "College not added")} - {escape(badge_line)}</div>
                            </div>
                            <div style="text-align:right;">
                                <div style="font-family:'Manrope',sans-serif;font-weight:800;font-size:1.2rem;">{ambassador["points"]} pts</div>
                                <div style="margin-top:5px;">{score_pill(gh, 'GitHub') if ambassador.get('github_username') else '<span class="pill">No GitHub</span>'}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty">No ambassadors have joined yet.</div>', unsafe_allow_html=True)

        section_label("Task portfolio")
        for task in tasks[:6]:
            total = task["total_submissions"] or 0
            approved = task["approved_count"] or 0
            pct = int((approved / total) * 100) if total else 0
            st.markdown(
                f"""
                <div class="task-card">
                    <div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start;">
                        <div>
                            {tag(task["task_type"].title(), TYPE_COLORS.get(task["task_type"], "#9b8cff"))}
                            <div style="font-family:'Manrope',sans-serif;font-size:1.08rem;font-weight:800;margin-top:8px;">{escape(task['title'])}</div>
                            <div style="color:#8c98b8;font-size:0.9rem;margin-top:5px;">{escape(task['description'] or 'No description added.')}</div>
                        </div>
                        <div style="text-align:right;">
                            <div style="font-family:'Manrope',sans-serif;font-size:1.15rem;font-weight:800;">{task['points_reward']} pts</div>
                            <div style="color:#8c98b8;font-size:0.78rem;">Deadline: {escape(task['deadline'] or 'Open')}</div>
                        </div>
                    </div>
                    <div style="margin-top:12px;" class="bar-track"><div class="bar-fill" style="width:{pct}%;"></div></div>
                    <div style="display:flex;justify-content:space-between;color:#8c98b8;font-size:0.82rem;margin-top:7px;">
                        <span>{total} submissions</span>
                        <span>{approved} approved</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        section_label("What needs attention")
        cards = [
            ("Review queue", f"{stats['pending_review']} submissions are waiting for scoring and feedback."),
            ("GitHub completion", f"{unlinked_count} ambassadors still have no public GitHub profile linked."),
            ("Program signal", f"{len(linked)} ambassadors can already be compared using GitHub evidence."),
        ]
        if tasks:
            cards.append(("Latest task", f"{tasks[0]['title']} is worth {tasks[0]['points_reward']} points."))
        for title, body in cards:
            st.markdown(
                f"""
                <div class="soft-card">
                    <div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:800;">{escape(title)}</div>
                    <div style="color:#8c98b8;margin-top:6px;">{escape(body)}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        section_label("Pending submissions")
        if pending:
            for item in pending[:5]:
                st.markdown(
                    f"""
                    <div class="queue-card">
                        <div style="font-family:'Manrope',sans-serif;font-weight:800;">{escape(item['ambassador_name'])}</div>
                        <div style="color:#8c98b8;font-size:0.84rem;margin-top:4px;">{escape(item['task_title'])}</div>
                        <div style="color:#ffb86b;font-size:0.8rem;margin-top:6px;">Worth {item['points_reward']} points</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty">Everything is reviewed. Nice pace.</div>', unsafe_allow_html=True)


def org_tasks_page(org):
    tasks = get_tasks(org["id"])
    section_label("Create a new task")
    with st.form("new_task"):
        col1, col2 = st.columns(2)
        title = col1.text_input("Task title")
        task_type = col2.selectbox("Type", list(TYPE_COLORS.keys()))
        description = st.text_area("Description", height=90)
        col3, col4 = st.columns(2)
        points = col3.number_input("Points reward", min_value=5, max_value=500, value=60, step=5)
        deadline = col4.date_input("Deadline")
        if st.form_submit_button("Create task", use_container_width=True):
            create_task(org["id"], title, description, task_type, points, deadline)
            st.success("Task created.")
            st.rerun()

    total_submissions = sum(task["total_submissions"] or 0 for task in tasks)
    section_label("Current workload")
    cols = st.columns(3)
    cols[0].markdown(metric_card(len(tasks), "Open tasks", "Programs in motion"), unsafe_allow_html=True)
    cols[1].markdown(metric_card(total_submissions, "Submissions", "Across all tasks"), unsafe_allow_html=True)
    cols[2].markdown(
        metric_card(sum(task["pending_count"] or 0 for task in tasks), "Pending reviews", "Watch response time"),
        unsafe_allow_html=True,
    )

    section_label("Task library")
    if not tasks:
        st.markdown('<div class="empty">No tasks yet. Create the first mission above.</div>', unsafe_allow_html=True)
        return
    for task in tasks:
        total = task["total_submissions"] or 0
        approved = task["approved_count"] or 0
        pending = task["pending_count"] or 0
        pct = int((approved / total) * 100) if total else 0
        st.markdown(
            f"""
            <div class="task-card">
                <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:14px;">
                    <div>
                        {tag(task["task_type"].title(), TYPE_COLORS.get(task["task_type"], "#9b8cff"))}
                        <div style="font-family:'Manrope',sans-serif;font-size:1.1rem;font-weight:800;margin-top:8px;">{escape(task['title'])}</div>
                        <div style="color:#8c98b8;font-size:0.9rem;margin-top:6px;">{escape(task['description'] or 'No description added.')}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-family:'Manrope',sans-serif;font-size:1.2rem;font-weight:800;">{task['points_reward']} pts</div>
                        <div style="color:#8c98b8;font-size:0.8rem;">Deadline: {escape(task['deadline'] or 'Open')}</div>
                    </div>
                </div>
                <div style="display:flex;gap:12px;flex-wrap:wrap;margin-top:12px;">
                    <span class="pill">{total} submitted</span>
                    <span class="pill">{approved} approved</span>
                    <span class="pill">{pending} pending</span>
                </div>
                <div style="margin-top:12px;" class="bar-track"><div class="bar-fill" style="width:{pct}%;"></div></div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def org_ambassadors_page(org):
    ambassadors = get_ambassadors_with_github(org["id"])
    section_label("Roster")
    search = st.text_input("Search ambassadors", placeholder="Search by name or college")
    sort_label = st.selectbox("Sort by", ["GitHub score", "Points", "Name"], index=0)

    filtered = ambassadors
    if search.strip():
        query = search.lower().strip()
        filtered = [
            ambassador
            for ambassador in ambassadors
            if query in ambassador["name"].lower() or query in (ambassador.get("college") or "").lower()
        ]

    if sort_label == "Points":
        filtered = sorted(filtered, key=lambda item: item.get("points", 0), reverse=True)
    elif sort_label == "Name":
        filtered = sorted(filtered, key=lambda item: item["name"].lower())
    else:
        filtered = sorted(filtered, key=lambda item: item.get("github_score") or -1, reverse=True)

    if not filtered:
        st.markdown('<div class="empty">No ambassadors matched that search.</div>', unsafe_allow_html=True)
        return

    for ambassador in filtered:
        badges = get_user_badges(ambassador["id"])
        badge_line = " ".join(f"{badge['icon']} {badge['name']}" for badge in badges[:3]) or "No badges yet"
        gh_score = ambassador.get("github_score") or 0
        gh_link = ambassador.get("github_username")
        tone = score_tone(gh_score)
        st.markdown(
            f"""
            <div class="leader-card">
                <div style="display:flex;justify-content:space-between;gap:14px;align-items:flex-start;">
                    <div class="profile-row" style="flex:1;">
                        {avatar(ambassador["name"], ambassador.get("avatar_color", "#6ea8fe"), 48)}
                        <div style="flex:1;">
                            <div style="font-family:'Manrope',sans-serif;font-size:1.05rem;font-weight:800;">{escape(ambassador["name"])}</div>
                            <div style="color:#8c98b8;font-size:0.85rem;">{escape(ambassador.get("college") or "College not added")} - {escape(ambassador["email"])}</div>
                            <div style="color:#8c98b8;font-size:0.82rem;margin-top:6px;">{escape(badge_line)}</div>
                            <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">{score_pill(ambassador.get("fit_score") or 0, 'Fit')} {pipeline_pill(ambassador.get("pipeline_status"))}</div>
                        </div>
                    </div>
                    <div style="text-align:right;min-width:190px;">
                        <div style="font-family:'Manrope',sans-serif;font-size:1.15rem;font-weight:800;">{ambassador['points']} pts</div>
                        <div style="margin-top:6px;">{score_pill(gh_score, 'GitHub') if gh_link else '<span class="pill">GitHub not linked</span>'}</div>
                        <div style="color:{tone};font-size:0.82rem;margin-top:7px;">{escape(ambassador.get('github_tier') or 'Awaiting analysis')}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        with st.expander(f"Update pipeline for {ambassador['name']}"):
            current_status = ambassador.get("pipeline_status") or "watch"
            status_index = ["watch", "shortlist", "high_potential"].index(current_status)
            with st.form(f"pipeline_{ambassador['id']}"):
                new_status = st.selectbox("Decision", ["watch", "shortlist", "high_potential"], index=status_index)
                notes = st.text_area("Notes", value=ambassador.get("pipeline_notes") or "", height=90, placeholder="Why is this person promising?")
                if st.form_submit_button("Save pipeline update", use_container_width=True):
                    save_pipeline_status(org["id"], ambassador["id"], new_status, notes)
                    st.success("Pipeline updated.")
                    st.rerun()


def org_github_page(org):
    ambassadors = get_ambassadors_with_github(org["id"])
    default_candidates = [amb["github_username"] for amb in ambassadors if amb.get("github_username")]
    linked = [amb for amb in ambassadors if amb.get("github_username")]
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">GitHub intelligence</div>
            <div class="hero-title">Assess a public GitHub profile in under two minutes</div>
            <div class="hero-subtitle">Use the snapshot to validate technical signals before a deeper interview or community call.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.2, 0.8], gap="large")
    with col1:
        quick_pick = st.selectbox("Quick pick from linked ambassadors", [""] + default_candidates)
        with st.form("github_lab"):
            username = st.text_input("GitHub username", value=quick_pick, placeholder="for example: torvalds")
            token = st.text_input("Token", type="password", placeholder="Optional, improves GitHub rate limits")
            submitted = st.form_submit_button("Run GitHub scan", use_container_width=True)
        if submitted and username.strip():
            key = username.lower().strip()
            with st.spinner(f"Analyzing @{username.strip()}"):
                st.session_state.gh_cache[key] = analyze_github(username, token or None)
            st.session_state.review_profile = key

        if st.session_state.review_profile and st.session_state.review_profile in st.session_state.gh_cache:
            render_github_analysis(st.session_state.gh_cache[st.session_state.review_profile])

    with col2:
        avg_score = int(sum((amb.get("github_score") or 0) for amb in linked) / len(linked)) if linked else 0
        strongest = max(linked, key=lambda amb: amb.get("github_score") or 0) if linked else None
        st.markdown(metric_card(len(linked), "Profiles linked", "Ready for analysis"), unsafe_allow_html=True)
        st.markdown(metric_card(avg_score, "Average GitHub score", "Across linked ambassadors"), unsafe_allow_html=True)
        st.markdown(
            """
            <div class="soft-card">
                <div style="font-family:'Manrope',sans-serif;font-weight:800;">How to pitch it</div>
                <div style="color:#8c98b8;margin-top:6px;">
                    One input, one verdict, one shortlist-ready summary. The flow keeps evaluator effort low while still surfacing real repository evidence.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if strongest:
            st.markdown(
                f"""
                <div class="soft-card">
                    <div style="font-family:'Manrope',sans-serif;font-weight:800;">Current strongest profile</div>
                    <div style="color:#8c98b8;margin-top:6px;">{escape(strongest['name'])} leads with {strongest.get('github_score') or 0}/100 and can be used as your internal benchmark.</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    section_label("Linked ambassador benchmarks")
    if not ambassadors:
        st.markdown('<div class="empty">No ambassadors yet.</div>', unsafe_allow_html=True)
        return

    ranked = sorted(ambassadors, key=lambda item: ((item.get("github_score") or -1), item.get("points", 0)), reverse=True)
    for ambassador in ranked:
        gh_score = ambassador.get("github_score") or 0
        label = ambassador.get("github_tier") or "Not analyzed"
        buttons = st.columns([1.4, 1.2, 0.8])
        buttons[0].markdown(
            f"""
            <div class="panel-card">
                <div style="font-family:'Manrope',sans-serif;font-weight:800;">{escape(ambassador['name'])}</div>
                <div style="color:#8c98b8;font-size:0.84rem;margin-top:4px;">@{escape(ambassador.get('github_username') or 'not-linked')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        buttons[1].markdown(metric_card(gh_score if ambassador.get("github_username") else "N/A", "GitHub score", label), unsafe_allow_html=True)
        with buttons[2]:
            if ambassador.get("github_username") and st.button("Open", key=f"open_gh_{ambassador['id']}", use_container_width=True):
                key = ambassador["github_username"].lower()
                if key not in st.session_state.gh_cache:
                    raw = ambassador.get("github_data")
                    if raw:
                        try:
                            st.session_state.gh_cache[key] = json.loads(raw)
                        except Exception:
                            st.session_state.gh_cache[key] = analyze_github(ambassador["github_username"])
                    else:
                        st.session_state.gh_cache[key] = analyze_github(ambassador["github_username"])
                st.session_state.review_profile = key
                st.rerun()


def org_review_page(org):
    pending = get_pending_submissions(org["id"])
    section_label("Review queue")
    if not pending:
        st.markdown('<div class="empty">All submissions are reviewed. Great turnaround.</div>', unsafe_allow_html=True)
        return

    for submission in pending:
        with st.expander(f"{submission['ambassador_name']} - {submission['task_title']} - {submission['points_reward']} pts"):
            left, right = st.columns([1.4, 0.8], gap="large")
            with left:
                st.markdown(f"**Ambassador**: {submission['ambassador_name']}")
                st.markdown(f"**College**: {submission.get('college') or 'Not added'}")
                st.markdown(f"**Submitted**: {submission['submitted_at'][:16]}")
                if submission.get("proof_text"):
                    st.markdown(
                        f"""
                        <div class="panel-card" style="margin-top:12px;">
                            <div style="font-family:'Manrope',sans-serif;font-weight:800;margin-bottom:6px;">Submission proof</div>
                            <div style="color:#8c98b8;">{escape(submission['proof_text'])}</div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                if submission.get("proof_link"):
                    st.markdown(f"[Open proof link]({submission['proof_link']})")
            with right:
                with st.form(f"review_{submission['id']}"):
                    score = st.slider("Points to award", 0, submission["points_reward"], submission["points_reward"])
                    feedback = st.text_area("Feedback", height=100)
                    approve_col, reject_col = st.columns(2)
                    if approve_col.form_submit_button("Approve", use_container_width=True):
                        review_submission(submission["id"], "approved", score, feedback, submission["ambassador_id"], score)
                        st.success("Submission approved.")
                        st.rerun()
                    if reject_col.form_submit_button("Reject", use_container_width=True):
                        review_submission(submission["id"], "rejected", 0, feedback, submission["ambassador_id"], 0)
                        st.warning("Submission rejected.")
                        st.rerun()


def shortlist_board_page(org):
    board = get_shortlist_board(org["id"])
    st.markdown(
        """
        <div class="hero-card">
            <div class="eyebrow">Shortlist board</div>
            <div class="hero-title">Turn signals into decisions</div>
            <div class="hero-subtitle">Use Fit Score, GitHub evidence, and your own notes to move ambassadors from watchlist to shortlist.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(3, gap="large")
    statuses = ["watch", "shortlist", "high_potential"]
    for col, status in zip(cols, statuses):
        label, tone = PIPELINE_STYLES[status]
        items = sorted(board[status], key=lambda item: item.get("fit_score") or 0, reverse=True)
        with col:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div style="display:flex;justify-content:space-between;align-items:center;gap:10px;">
                        <div style="font-family:'Manrope',sans-serif;font-size:1rem;font-weight:800;color:{tone};">{label}</div>
                        <div class="pill">{len(items)} ambassadors</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if not items:
                st.markdown('<div class="empty">No ambassadors in this lane yet.</div>', unsafe_allow_html=True)
            for ambassador in items:
                st.markdown(
                    f"""
                    <div class="task-card">
                        <div style="display:flex;align-items:flex-start;gap:12px;">
                            {avatar(ambassador["name"], ambassador.get("avatar_color", tone), 42)}
                            <div style="flex:1;">
                                <div style="font-family:'Manrope',sans-serif;font-weight:800;">{escape(ambassador['name'])}</div>
                                <div style="color:#8c98b8;font-size:0.82rem;margin-top:3px;">{escape(ambassador.get('college') or 'College not added')}</div>
                                <div style="margin-top:8px;display:flex;gap:8px;flex-wrap:wrap;">
                                    {score_pill(ambassador.get("fit_score") or 0, "Fit")}
                                    {score_pill(ambassador.get("github_score") or 0, "GitHub") if ambassador.get("github_username") else '<span class="pill">No GitHub</span>'}
                                </div>
                                <div style="color:#8c98b8;font-size:0.82rem;margin-top:8px;">{escape((ambassador.get("pipeline_notes") or "No notes added yet.")[:140])}</div>
                            </div>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


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


def render_org_app(user):
    fresh_user = get_user(user["id"]) or user
    st.session_state.user = fresh_user
    org = get_org(fresh_user["org_id"])
    page = app_sidebar(
        fresh_user,
        org,
        {
            "Overview": "overview",
            "GitHub Lab": "github",
            "Ambassadors": "ambassadors",
            "Shortlist Board": "shortlist",
            "Tasks": "tasks",
            "Review": "review",
            "Leaderboard": "leaderboard",
        },
        "Organization admin",
    )
    if page == "overview":
        org_overview(org, fresh_user)
    elif page == "github":
        org_github_page(org)
    elif page == "ambassadors":
        org_ambassadors_page(org)
    elif page == "shortlist":
        shortlist_board_page(org)
    elif page == "tasks":
        org_tasks_page(org)
    elif page == "review":
        org_review_page(org)
    else:
        leaderboard_page(org["id"], "Team performance and GitHub signal")
