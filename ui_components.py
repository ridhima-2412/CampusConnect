from html import escape

import streamlit as st

from database import get_conn
from helpers import get_ambassador_stats, get_user_badges


TYPE_COLORS = {
    "referral": "#f59e0b",
    "promotion": "#ef4444",
    "content": "#6ea8fe",
    "event": "#34d3b4",
    "other": "#9b8cff",
}


def initials(name):
    parts = [part[0].upper() for part in str(name).split()[:2] if part]
    return "".join(parts) or "CC"


def avatar(name, color="#6ea8fe", size=42):
    return (
        f'<div class="avatar" style="width:{size}px;height:{size}px;background:{color};'
        f'font-size:{max(14, int(size * 0.34))}px;">{escape(initials(name))}</div>'
    )


def metric_card(value, label, note=""):
    note_html = f'<div class="metric-note">{escape(str(note))}</div>' if note else ""
    return (
        '<div class="metric-card">'
        f'<div class="metric-value">{escape(str(value))}</div>'
        f'<div class="metric-label">{escape(label)}</div>'
        f"{note_html}"
        "</div>"
    )


def tag(text, tone):
    return (
        f'<span class="tag" style="background:{tone}18;color:{tone};'
        f'border:1px solid {tone}33;">{escape(text)}</span>'
    )


def score_tone(score):
    if score >= 75:
        return "#34d3b4"
    if score >= 55:
        return "#ffb86b"
    return "#ff6b81"


def score_pill(score, label="score"):
    tone = score_tone(score)
    return (
        f'<span class="pill" style="color:{tone};border-color:{tone}33;background:{tone}12;">'
        f"{escape(str(score))}/100 {escape(label)}</span>"
    )


def section_label(text):
    st.markdown(f'<div class="section-label">{escape(text)}</div>', unsafe_allow_html=True)


def app_sidebar(user, org, pages, role_label):
    with st.sidebar:
        st.markdown(
            f"""
            <div class="panel-card">
                <div class="profile-row">
                    {avatar(user["name"], user.get("avatar_color", "#6ea8fe"), 46)}
                    <div>
                        <div style="font-family:'Manrope',sans-serif;font-weight:800;">{escape(user["name"])}</div>
                        <div style="color:#8c98b8;font-size:0.85rem;">{escape(role_label)}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if org:
            st.markdown(
                f"""
                <div class="panel-card">
                    <div class="eyebrow">Organization</div>
                    <div style="font-family:'Manrope',sans-serif;font-size:1.15rem;font-weight:800;margin-top:4px;">{escape(org["name"])}</div>
                    <div style="margin-top:12px;font-size:0.78rem;color:#8c98b8;">Invite code</div>
                    <div class="invite-box">{escape(org["invite_code"])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        page = st.radio("", list(pages.keys()), label_visibility="collapsed")
        if st.button("Log out", use_container_width=True):
            st.session_state.user = None
            st.session_state.review_profile = None
            st.rerun()
    return pages[page]


def fetch_badge_catalog():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM badges ORDER BY condition_value")
    badges = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return badges


def badge_progress(user, org_id):
    stats = get_ambassador_stats(user["id"], org_id)
    progress_items = []
    earned_ids = {badge["id"] for badge in get_user_badges(user["id"])}
    for badge in fetch_badge_catalog():
        if badge["id"] in earned_ids:
            continue
        if badge["condition_type"] == "tasks_completed":
            current = stats["tasks_done"]
        elif badge["condition_type"] == "points":
            current = user.get("points", 0)
        else:
            current = user.get("streak", 0)
        pct = min(100, int((current / badge["condition_value"]) * 100)) if badge["condition_value"] else 0
        progress_items.append(
            {
                "name": badge["name"],
                "description": badge["description"],
                "current": current,
                "target": badge["condition_value"],
                "pct": pct,
                "icon": badge["icon"],
            }
        )
    return progress_items[:3]


def next_priority(tasks):
    available = [task for task in tasks if not task["sub_id"]]
    if not available:
        return None
    return sorted(available, key=lambda item: item["points_reward"], reverse=True)[0]
