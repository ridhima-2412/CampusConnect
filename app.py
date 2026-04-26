import streamlit as st
from database import init_db
from helpers import *

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CampusConnect",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Global Styles ───────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
h1, h2, h3 { font-family: 'Space Grotesk', sans-serif; }

.main { background: #0f0f13; }

.metric-card {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    border: 1px solid #2a2a4a;
    border-radius: 16px;
    padding: 24px;
    text-align: center;
}
.metric-card .value {
    font-size: 2.4rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    background: linear-gradient(135deg, #818cf8, #c084fc);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.metric-card .label {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

.task-card {
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 18px 20px;
    margin-bottom: 12px;
    transition: border-color 0.2s;
}
.task-card:hover { border-color: #6366f1; }

.badge-pill {
    display: inline-block;
    background: #1e1b4b;
    border: 1px solid #4338ca;
    color: #a5b4fc;
    border-radius: 99px;
    padding: 3px 12px;
    font-size: 0.78rem;
    font-weight: 500;
    margin: 2px;
}

.rank-row {
    display: flex;
    align-items: center;
    gap: 16px;
    background: #1a1a2e;
    border: 1px solid #2a2a4a;
    border-radius: 12px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.rank-num {
    font-size: 1.4rem;
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    color: #6366f1;
    width: 36px;
}
.rank-name { font-weight: 600; color: #e2e8f0; flex: 1; }
.rank-pts {
    font-weight: 700;
    font-family: 'Space Grotesk', sans-serif;
    color: #a78bfa;
}

.section-header {
    font-family: 'Space Grotesk', sans-serif;
    font-size: 1.1rem;
    font-weight: 600;
    color: #c7d2fe;
    border-left: 3px solid #6366f1;
    padding-left: 12px;
    margin: 28px 0 16px 0;
}

.status-approved { color: #34d399; font-weight: 600; }
.status-pending  { color: #fbbf24; font-weight: 600; }
.status-rejected { color: #f87171; font-weight: 600; }

.invite-box {
    background: #1e1b4b;
    border: 1px dashed #4338ca;
    border-radius: 10px;
    padding: 14px 20px;
    font-family: 'Space Grotesk', monospace;
    font-size: 1.2rem;
    font-weight: 700;
    color: #a5b4fc;
    text-align: center;
    letter-spacing: 0.15em;
}

div[data-testid="stSidebar"] {
    background: #0d0d1a;
    border-right: 1px solid #1e1e3a;
}

.stButton>button {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
    border-radius: 8px;
    font-weight: 600;
    font-family: 'Space Grotesk', sans-serif;
    transition: opacity 0.2s;
}
.stButton>button:hover { opacity: 0.85; }

.type-tag {
    font-size: 0.72rem;
    padding: 2px 10px;
    border-radius: 99px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
</style>
""", unsafe_allow_html=True)

# ─── Init DB ─────────────────────────────────────────────────────────────────
init_db()

# ─── Session State ───────────────────────────────────────────────────────────
if 'user' not in st.session_state:
    st.session_state.user = None
if 'page' not in st.session_state:
    st.session_state.page = 'login'

# ─── Helpers ─────────────────────────────────────────────────────────────────
TYPE_COLORS = {
    'referral': '#f59e0b',
    'promotion': '#ec4899',
    'content': '#3b82f6',
    'event': '#10b981',
    'other': '#6366f1'
}

def type_badge(t):
    c = TYPE_COLORS.get(t, '#6366f1')
    return f'<span style="background:{c}22;color:{c};border:1px solid {c}44;" class="type-tag">{t}</span>'

def avatar(name, color='#6366f1'):
    initials = ''.join([w[0].upper() for w in name.split()[:2]])
    return f'<div style="width:38px;height:38px;border-radius:50%;background:{color};display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85rem;color:white;flex-shrink:0;">{initials}</div>'

def rank_emoji(i):
    return ['🥇','🥈','🥉'][i] if i < 3 else f'#{i+1}'

# ─── Auth Page ───────────────────────────────────────────────────────────────
def show_auth():
    st.markdown("""
    <div style="text-align:center;padding:40px 0 20px;">
        <div style="font-size:3rem">🎓</div>
        <h1 style="font-family:'Space Grotesk',sans-serif;font-size:2.4rem;background:linear-gradient(135deg,#818cf8,#c084fc);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin:0;">
            CampusConnect
        </h1>
        <p style="color:#94a3b8;margin-top:8px;">The campus ambassador platform that actually works.</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["🔐 Login", "🏢 Register as Org", "🙋 Join as Ambassador"])

    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="org@demo.com or arjun@demo.com")
            password = st.text_input("Password", type="password", placeholder="demo123")
            submitted = st.form_submit_button("Login →", use_container_width=True)
            if submitted:
                user = login_user(email, password)
                if user:
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("Invalid credentials.")
        st.markdown("""
        <div style="background:#1a1a2e;border-radius:10px;padding:14px;margin-top:12px;">
            <p style="color:#94a3b8;font-size:0.82rem;margin:0 0 6px;">🎭 Demo accounts (password: <code>demo123</code>)</p>
            <p style="color:#a5b4fc;font-size:0.82rem;margin:2px 0;"><b>Org:</b> org@demo.com</p>
            <p style="color:#a5b4fc;font-size:0.82rem;margin:2px 0;"><b>Ambassador:</b> arjun@demo.com</p>
        </div>
        """, unsafe_allow_html=True)

    with tab2:
        with st.form("reg_org"):
            name = st.text_input("Your Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            org_name = st.text_input("Organization Name")
            org_desc = st.text_area("Organization Description", height=80)
            if st.form_submit_button("Create Organization →", use_container_width=True):
                ok, msg = register_org(name, email, password, org_name, org_desc)
                st.success(msg) if ok else st.error(msg)

    with tab3:
        with st.form("reg_amb"):
            name = st.text_input("Your Name")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            college = st.text_input("College Name")
            invite_code = st.text_input("Invite Code (from organization)")
            if st.form_submit_button("Join Program →", use_container_width=True):
                ok, msg = register_ambassador(name, email, password, college, invite_code)
                st.success(msg) if ok else st.error(msg)

# ─── ORG DASHBOARD ───────────────────────────────────────────────────────────
def show_org_dashboard():
    user = st.session_state.user
    org = get_org(user['org_id'])

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px;">
            {avatar(user['name'], user['avatar_color'])}
            <div style="margin-top:10px;">
                <div style="font-weight:700;color:#e2e8f0;">{user['name']}</div>
                <div style="font-size:0.78rem;color:#94a3b8;">{org['name']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        pages = {"📊 Dashboard": "dash", "📋 Tasks": "tasks", "👥 Ambassadors": "ambs",
                 "🔔 Review": "review", "🏆 Leaderboard": "leaderboard"}
        page = st.radio("Navigate", list(pages.keys()), label_visibility="collapsed")
        active = pages[page]

        st.markdown("---")
        st.markdown(f"""
        <div style="margin-top:8px;">
            <div style="font-size:0.78rem;color:#94a3b8;margin-bottom:6px;">Invite Code</div>
            <div class="invite-box">{org['invite_code']}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    # Main content
    if active == "dash":
        org_dashboard_home(org, user)
    elif active == "tasks":
        org_tasks(org, user)
    elif active == "ambs":
        org_ambassadors(org)
    elif active == "review":
        org_review(org)
    elif active == "leaderboard":
        show_leaderboard(org['id'])

def org_dashboard_home(org, user):
    st.markdown(f"<h2 style='margin-bottom:4px;'>Welcome back 👋</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8;margin-top:0;'>Managing <b style='color:#c7d2fe;'>{org['name']}</b> ambassador program</p>", unsafe_allow_html=True)

    stats = get_org_stats(org['id'])
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, stats['total_ambassadors'], "Total Ambassadors"),
        (c2, stats['total_tasks'], "Active Tasks"),
        (c3, stats['approved_submissions'], "Approved Tasks"),
        (c4, stats['pending_review'], "Pending Review"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="value">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<div class='section-header'>Top Performers</div>", unsafe_allow_html=True)
    ambs = get_ambassadors(org['id'])[:5]
    for i, a in enumerate(ambs):
        st.markdown(f"""
        <div class="rank-row">
            <div style="font-size:1.4rem;width:36px;">{rank_emoji(i)}</div>
            {avatar(a['name'], a['avatar_color'])}
            <div class="rank-name">{a['name']} <span style="font-size:0.78rem;color:#64748b;">· {a['college'] or 'N/A'}</span></div>
            <div style="color:#94a3b8;font-size:0.85rem;">{a['tasks_done']} tasks</div>
            <div class="rank-pts">{a['points']} pts</div>
        </div>
        """, unsafe_allow_html=True)

def org_tasks(org, user):
    st.markdown("<h2>Task Management</h2>", unsafe_allow_html=True)

    with st.expander("➕ Create New Task", expanded=False):
        with st.form("new_task"):
            col1, col2 = st.columns(2)
            title = col1.text_input("Task Title")
            task_type = col2.selectbox("Type", ['referral','promotion','content','event','other'])
            desc = st.text_area("Description", height=90)
            col3, col4 = st.columns(2)
            points = col3.number_input("Points Reward", min_value=5, max_value=500, value=50, step=5)
            deadline = col4.date_input("Deadline")
            if st.form_submit_button("Create Task →", use_container_width=True):
                create_task(org['id'], title, desc, task_type, points, deadline)
                st.success("Task created!")
                st.rerun()

    st.markdown("<div class='section-header'>All Tasks</div>", unsafe_allow_html=True)
    tasks = get_tasks(org['id'])
    if not tasks:
        st.info("No tasks yet. Create your first task above!")
    for t in tasks:
        completion = int((t['approved_count'] or 0) / max(t['total_submissions'] or 1, 1) * 100)
        st.markdown(f"""
        <div class="task-card">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px;">
                {type_badge(t['task_type'])}
                <span style="font-weight:600;color:#e2e8f0;">{t['title']}</span>
                <span style="margin-left:auto;color:#a78bfa;font-weight:700;font-family:'Space Grotesk',sans-serif;">{t['points_reward']} pts</span>
            </div>
            <p style="color:#94a3b8;font-size:0.85rem;margin:0 0 10px;">{t['description'] or ''}</p>
            <div style="display:flex;gap:20px;font-size:0.82rem;">
                <span style="color:#fbbf24;">⏳ {t['pending_count'] or 0} pending</span>
                <span style="color:#34d399;">✅ {t['approved_count'] or 0} approved</span>
                <span style="color:#94a3b8;">📅 Due {t['deadline'] or 'N/A'}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

def org_ambassadors(org):
    st.markdown("<h2>Ambassadors</h2>", unsafe_allow_html=True)
    ambs = get_ambassadors(org['id'])
    if not ambs:
        st.info("No ambassadors yet. Share your invite code!")
        return
    for a in ambs:
        badges = get_user_badges(a['id'])
        badge_html = ' '.join([f"<span class='badge-pill'>{b['icon']} {b['name']}</span>" for b in badges])
        st.markdown(f"""
        <div class="task-card">
            <div style="display:flex;align-items:center;gap:12px;">
                {avatar(a['name'], a['avatar_color'])}
                <div style="flex:1;">
                    <div style="font-weight:600;color:#e2e8f0;">{a['name']}</div>
                    <div style="font-size:0.8rem;color:#64748b;">{a['college'] or 'N/A'} · {a['email']}</div>
                </div>
                <div style="text-align:right;">
                    <div style="font-weight:700;color:#a78bfa;font-family:'Space Grotesk',sans-serif;">{a['points']} pts</div>
                    <div style="font-size:0.78rem;color:#94a3b8;">🔥 {a['streak']} day streak</div>
                </div>
            </div>
            <div style="margin-top:10px;">{badge_html}</div>
        </div>
        """, unsafe_allow_html=True)

def org_review(org):
    st.markdown("<h2>Review Submissions</h2>", unsafe_allow_html=True)
    subs = get_pending_submissions(org['id'])
    if not subs:
        st.success("🎉 All caught up! No pending submissions.")
        return
    for s in subs:
        with st.expander(f"📥 {s['ambassador_name']} → {s['task_title']}"):
            col1, col2 = st.columns([3,1])
            col1.markdown(f"**College:** {s['college'] or 'N/A'}")
            col1.markdown(f"**Submitted:** {s['submitted_at'][:16]}")
            if s['proof_text']:
                col1.markdown(f"**Proof:** {s['proof_text']}")
            if s['proof_link']:
                col1.markdown(f"**Link:** [{s['proof_link']}]({s['proof_link']})")
            col2.metric("Max Points", s['points_reward'])

            with st.form(f"review_{s['id']}"):
                score = st.slider("Score", 0, s['points_reward'], s['points_reward'])
                feedback = st.text_input("Feedback (optional)")
                c1, c2 = st.columns(2)
                approve = c1.form_submit_button("✅ Approve", use_container_width=True)
                reject = c2.form_submit_button("❌ Reject", use_container_width=True)
                if approve:
                    review_submission(s['id'], 'approved', score, feedback, s['ambassador_id'], score)
                    st.success("Approved!")
                    st.rerun()
                if reject:
                    review_submission(s['id'], 'rejected', 0, feedback, s['ambassador_id'], 0)
                    st.warning("Rejected.")
                    st.rerun()

def show_leaderboard(org_id):
    st.markdown("<h2>🏆 Leaderboard</h2>", unsafe_allow_html=True)
    ambs = get_ambassadors(org_id)
    for i, a in enumerate(ambs):
        bg = ['#1e1b4b','#1a1a2e','#1a1a2e'][min(i,2)]
        border = ['#6366f1','#94a3b8','#b45309'][min(i,2)] if i < 3 else '#2a2a4a'
        badges = get_user_badges(a['id'])
        badge_html = ''.join([b['icon'] for b in badges[:4]])
        st.markdown(f"""
        <div style="background:{bg};border:1px solid {border};border-radius:14px;padding:18px 22px;margin-bottom:12px;display:flex;align-items:center;gap:16px;">
            <div style="font-size:1.8rem;width:40px;text-align:center;">{rank_emoji(i)}</div>
            {avatar(a['name'], a['avatar_color'])}
            <div style="flex:1;">
                <div style="font-weight:700;color:#e2e8f0;font-family:'Space Grotesk',sans-serif;">{a['name']}</div>
                <div style="font-size:0.78rem;color:#64748b;">{a['college'] or 'N/A'} · {badge_html}</div>
            </div>
            <div style="text-align:right;">
                <div style="font-size:1.5rem;font-weight:800;color:#a78bfa;font-family:'Space Grotesk',sans-serif;">{a['points']}</div>
                <div style="font-size:0.75rem;color:#94a3b8;">points · 🔥{a['streak']}d</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ─── AMBASSADOR DASHBOARD ────────────────────────────────────────────────────
def show_ambassador_dashboard():
    user = st.session_state.user
    org = get_org(user['org_id'])

    with st.sidebar:
        st.markdown(f"""
        <div style="padding:16px 0 8px;">
            {avatar(user['name'], user['avatar_color'])}
            <div style="margin-top:10px;">
                <div style="font-weight:700;color:#e2e8f0;">{user['name']}</div>
                <div style="font-size:0.78rem;color:#94a3b8;">{user.get('college','') or 'Ambassador'}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("---")
        pages = {"🏠 My Dashboard": "home", "📋 Tasks": "tasks", "🏅 My Badges": "badges", "🏆 Leaderboard": "leaderboard"}
        page = st.radio("Navigate", list(pages.keys()), label_visibility="collapsed")
        active = pages[page]
        st.markdown("---")
        if st.button("Logout", use_container_width=True):
            st.session_state.user = None
            st.rerun()

    if active == "home":
        amb_home(user, org)
    elif active == "tasks":
        amb_tasks(user, org)
    elif active == "badges":
        amb_badges(user)
    elif active == "leaderboard":
        show_leaderboard(org['id'])

def amb_home(user, org):
    st.markdown(f"<h2>Hey {user['name'].split()[0]} 👋</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='color:#94a3b8;margin-top:0;'>Ambassador at <b style='color:#c7d2fe;'>{org['name']}</b></p>", unsafe_allow_html=True)

    stats = get_ambassador_stats(user['id'], org['id'])
    c1, c2, c3, c4 = st.columns(4)
    for col, val, label in [
        (c1, stats['points'], "Total Points"),
        (c2, f"🔥 {stats['streak']}", "Day Streak"),
        (c3, stats['tasks_done'], "Tasks Done"),
        (c4, stats['pending'], "In Review"),
    ]:
        col.markdown(f"""
        <div class="metric-card">
            <div class="value">{val}</div>
            <div class="label">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    badges = get_user_badges(user['id'])
    if badges:
        st.markdown("<div class='section-header'>Your Badges</div>", unsafe_allow_html=True)
        cols = st.columns(min(len(badges), 4))
        for i, b in enumerate(badges[:4]):
            cols[i].markdown(f"""
            <div style="background:#1e1b4b;border:1px solid #4338ca;border-radius:12px;padding:14px;text-align:center;">
                <div style="font-size:1.8rem;">{b['icon']}</div>
                <div style="font-size:0.8rem;color:#a5b4fc;font-weight:600;margin-top:6px;">{b['name']}</div>
            </div>
            """, unsafe_allow_html=True)

def amb_tasks(user, org):
    st.markdown("<h2>My Tasks</h2>", unsafe_allow_html=True)
    tasks = get_ambassador_tasks(user['id'], org['id'])

    pending_tasks = [t for t in tasks if not t['sub_id']]
    submitted_tasks = [t for t in tasks if t['sub_id']]

    st.markdown("<div class='section-header'>Available Tasks</div>", unsafe_allow_html=True)
    if not pending_tasks:
        st.info("You've submitted all available tasks. 🎉")
    for t in pending_tasks:
        with st.expander(f"{type_badge(t['task_type'])} **{t['title']}** · {t['points_reward']} pts", expanded=False):
            st.markdown(f"**Description:** {t['description']}")
            st.markdown(f"**Deadline:** {t['deadline']}")
            with st.form(f"submit_{t['id']}"):
                proof_text = st.text_area("Describe what you did", height=80)
                proof_link = st.text_input("Proof Link (screenshot, post URL, etc.)")
                if st.form_submit_button("Submit for Review →", use_container_width=True):
                    ok, msg = submit_task(t['id'], user['id'], proof_text, proof_link)
                    st.success(msg) if ok else st.error(msg)
                    st.rerun()

    st.markdown("<div class='section-header'>Submitted Tasks</div>", unsafe_allow_html=True)
    for t in submitted_tasks:
        status_class = f"status-{t['sub_status']}"
        icon = {'approved':'✅','pending':'⏳','rejected':'❌'}.get(t['sub_status'],'?')
        st.markdown(f"""
        <div class="task-card">
            <div style="display:flex;align-items:center;gap:10px;">
                {type_badge(t['task_type'])}
                <span style="font-weight:600;color:#e2e8f0;">{t['title']}</span>
                <span class="{status_class}" style="margin-left:auto;">{icon} {t['sub_status'].capitalize()}</span>
            </div>
            <div style="margin-top:8px;font-size:0.85rem;color:#94a3b8;">
                Score: <b style="color:#a78bfa;">{t['sub_score'] or 0} pts</b>
                {f"· Feedback: {t['feedback']}" if t['feedback'] else ""}
            </div>
        </div>
        """, unsafe_allow_html=True)

def amb_badges(user):
    st.markdown("<h2>🏅 My Badges</h2>", unsafe_allow_html=True)
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM badges")
    all_badges = [dict(b) for b in c.fetchall()]
    conn.close()
    earned = {b['id'] for b in get_user_badges(user['id'])}

    cols = st.columns(3)
    for i, b in enumerate(all_badges):
        is_earned = b['id'] in earned
        opacity = "1" if is_earned else "0.35"
        border = "#4338ca" if is_earned else "#2a2a4a"
        with cols[i % 3]:
            st.markdown(f"""
            <div style="background:#1a1a2e;border:1px solid {border};border-radius:14px;padding:20px;text-align:center;margin-bottom:14px;opacity:{opacity};">
                <div style="font-size:2.4rem;">{b['icon']}</div>
                <div style="font-weight:700;color:#e2e8f0;font-family:'Space Grotesk',sans-serif;margin-top:8px;">{b['name']}</div>
                <div style="font-size:0.78rem;color:#94a3b8;margin-top:4px;">{b['description']}</div>
                {'<div style="font-size:0.72rem;color:#34d399;margin-top:8px;font-weight:600;">✓ EARNED</div>' if is_earned else '<div style="font-size:0.72rem;color:#475569;margin-top:8px;">Locked</div>'}
            </div>
            """, unsafe_allow_html=True)

# ─── Router ──────────────────────────────────────────────────────────────────
if not st.session_state.user:
    show_auth()
elif st.session_state.user['role'] == 'org':
    show_org_dashboard()
else:
    show_ambassador_dashboard()
