import json
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import streamlit as st


GITHUB_API_BASE = "https://api.github.com"


def _github_request(path, token=None):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "CampusConnect",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{GITHUB_API_BASE}{path}", headers=headers)
    with urlopen(request, timeout=15) as response:
        return json.loads(response.read().decode("utf-8"))


def _safe_int(value):
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _parse_github_date(value):
    if not value:
        return None
    try:
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _score_bucket(score):
    if score >= 85:
        return "High-conviction"
    if score >= 70:
        return "Strong"
    if score >= 55:
        return "Promising"
    return "Needs proof"


def _role_hint(craft, consistency, reach):
    if craft >= 22 and consistency >= 18:
        return "Builder"
    if reach >= 10 and consistency >= 16:
        return "Community catalyst"
    if craft >= 18 and reach >= 8:
        return "Technical storyteller"
    return "Emerging contributor"


def _score_profile(user, repos):
    public_repos = _safe_int(user.get("public_repos"))
    followers = _safe_int(user.get("followers"))
    following = _safe_int(user.get("following"))
    original_repos = [repo for repo in repos if not repo.get("fork")]
    stars = sum(_safe_int(repo.get("stargazers_count")) for repo in original_repos)
    forks = sum(_safe_int(repo.get("forks_count")) for repo in original_repos)
    watchers = sum(_safe_int(repo.get("watchers_count")) for repo in original_repos)
    languages = sorted({repo.get("language") for repo in repos if repo.get("language")})
    now = datetime.now(timezone.utc)
    recent_repos = 0
    active_this_year = 0

    for repo in repos:
        pushed = _parse_github_date(repo.get("pushed_at"))
        if not pushed:
            continue
        days_since_push = (now - pushed).days
        if days_since_push <= 180:
            recent_repos += 1
        if days_since_push <= 365:
            active_this_year += 1

    profile_depth = min(
        20,
        (6 if user.get("bio") else 0)
        + (4 if user.get("company") else 0)
        + (4 if user.get("blog") else 0)
        + (3 if user.get("location") else 0)
        + (3 if user.get("name") else 0),
    )
    craft = min(30, len(original_repos) * 2 + min(stars, 12) + min(forks, 6))
    consistency = min(25, recent_repos * 3 + active_this_year + min(public_repos, 6))
    reach = min(15, min(followers, 20) // 2 + min(watchers, 6) + min(stars, 6))
    breadth = min(10, len(languages) * 2 + (2 if len(languages) >= 4 else 0))
    overall_score = min(100, profile_depth + craft + consistency + reach + breadth)

    breakdown = [
        {"label": "Profile", "score": profile_depth, "max": 20},
        {"label": "Craft", "score": craft, "max": 30},
        {"label": "Consistency", "score": consistency, "max": 25},
        {"label": "Reach", "score": reach, "max": 15},
        {"label": "Breadth", "score": breadth, "max": 10},
    ]

    strengths = []
    risks = []

    if len(original_repos) >= 5:
        strengths.append("Maintains several original projects instead of only forks")
    if recent_repos >= 3:
        strengths.append("Shows recent activity, which reduces stale-profile risk")
    if len(languages) >= 3:
        strengths.append("Demonstrates range across multiple languages or stacks")
    if followers >= 20 or stars >= 10:
        strengths.append("Has visible external validation through followers or repo traction")

    if not user.get("bio"):
        risks.append("Profile bio is missing, so context and positioning are weaker")
    if recent_repos == 0:
        risks.append("No recently pushed repositories were detected")
    if len(original_repos) < 2:
        risks.append("Very few original repositories makes technical depth harder to verify")
    if not languages:
        risks.append("Repository language signals are limited")

    if not strengths:
        strengths.append("Solid starting point with room to sharpen public signals")
    if not risks:
        risks.append("No major public signal gaps were detected")

    if overall_score >= 80:
        verdict = "Ready to shortlist for high-ownership ambassador work."
    elif overall_score >= 65:
        verdict = "Strong candidate with enough public proof to move forward."
    elif overall_score >= 50:
        verdict = "Worth considering, but review one or two repositories before deciding."
    else:
        verdict = "Use the score as a prompt for follow-up rather than a final decision."

    return {
        "overall_score": overall_score,
        "tier": _score_bucket(overall_score),
        "role_hint": _role_hint(craft, consistency, reach),
        "verdict": verdict,
        "breakdown": breakdown,
        "metrics": {
            "public_repos": public_repos,
            "followers": followers,
            "following": following,
            "stars": stars,
            "forks": forks,
            "watchers": watchers,
            "languages": languages,
            "original_repos": len(original_repos),
            "recent_repos": recent_repos,
            "active_this_year": active_this_year,
        },
        "strengths": strengths,
        "risks": risks,
    }


def analyze_github(username, token=None):
    username = (username or "").strip()
    if not username:
        return {"found": False, "username": "", "error": "Enter a GitHub username to continue."}

    encoded_user = quote(username)
    try:
        user = _github_request(f"/users/{encoded_user}", token=token)
        repos = _github_request(f"/users/{encoded_user}/repos?per_page=100&sort=updated", token=token)
    except HTTPError as exc:
        if exc.code == 404:
            return {"found": False, "username": username, "error": f"GitHub user @{username} was not found."}
        if exc.code == 403:
            return {
                "found": False,
                "username": username,
                "error": "GitHub rate limit reached. Add a token to unlock higher request limits.",
            }
        return {"found": False, "username": username, "error": f"GitHub API error: HTTP {exc.code}."}
    except URLError:
        return {
            "found": False,
            "username": username,
            "error": "GitHub could not be reached right now. Check the connection and try again.",
        }
    except Exception as exc:
        return {"found": False, "username": username, "error": f"Unexpected GitHub analysis error: {exc}"}

    repos = repos if isinstance(repos, list) else []
    scored = _score_profile(user, repos)
    top_repos = sorted(
        repos,
        key=lambda repo: (
            _safe_int(repo.get("stargazers_count")),
            _safe_int(repo.get("forks_count")),
            _safe_int(repo.get("watchers_count")),
        ),
        reverse=True,
    )[:5]

    return {
        "found": True,
        "username": user.get("login", username),
        "profile_url": user.get("html_url"),
        "name": user.get("name") or user.get("login") or username,
        "bio": user.get("bio") or "",
        "avatar_url": user.get("avatar_url"),
        "company": user.get("company") or "",
        "location": user.get("location") or "",
        "tier": scored["tier"],
        "role_hint": scored["role_hint"],
        "verdict": scored["verdict"],
        "overall_score": scored["overall_score"],
        "breakdown": scored["breakdown"],
        "metrics": scored["metrics"],
        "strengths": scored["strengths"],
        "risks": scored["risks"],
        "top_repos": [
            {
                "name": repo.get("name"),
                "url": repo.get("html_url"),
                "stars": _safe_int(repo.get("stargazers_count")),
                "forks": _safe_int(repo.get("forks_count")),
                "language": repo.get("language") or "Unknown",
                "updated_at": repo.get("pushed_at"),
            }
            for repo in top_repos
        ],
    }


def render_github_analysis(data):
    if not data:
        return
    if not data.get("found"):
        st.error(data.get("error", "Unable to analyze this GitHub profile."))
        return

    metrics = data.get("metrics", {})
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">GitHub intelligence snapshot</div>
            <div class="hero-title">{data.get("name", data.get("username", "GitHub user"))}</div>
            <div class="hero-subtitle">@{data.get("username", "")} - {data.get("role_hint", "Contributor")}</div>
            <div class="hero-note">{data.get("verdict", "")}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    cols = st.columns(4)
    cols[0].markdown(_metric_card(f"{data.get('overall_score', 0)}/100", "Overall score"), unsafe_allow_html=True)
    cols[1].markdown(_metric_card(data.get("tier", "Unknown"), "Tier"), unsafe_allow_html=True)
    cols[2].markdown(_metric_card(metrics.get("recent_repos", 0), "Active repos"), unsafe_allow_html=True)
    cols[3].markdown(_metric_card(metrics.get("followers", 0), "Followers"), unsafe_allow_html=True)

    if data.get("profile_url"):
        st.markdown(f"[Open GitHub profile]({data['profile_url']})")

    bio = data.get("bio") or "No bio added yet."
    extra = " - ".join([item for item in [data.get("company"), data.get("location")] if item])
    st.markdown(f"**Profile summary**  \n{bio}" + (f"  \n{extra}" if extra else ""))

    left, right = st.columns([1.2, 1])
    with left:
        st.markdown("#### Score breakdown")
        for item in data.get("breakdown", []):
            pct = 0 if not item.get("max") else int(item["score"] / item["max"] * 100)
            st.markdown(
                f"""
                <div class="bar-row">
                    <div class="bar-head">
                        <span>{item['label']}</span>
                        <span>{item['score']}/{item['max']}</span>
                    </div>
                    <div class="bar-track">
                        <div class="bar-fill" style="width:{pct}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with right:
        st.markdown("#### What stands out")
        for item in data.get("strengths", []):
            st.markdown(f"- {item}")
        st.markdown("#### What to verify")
        for item in data.get("risks", []):
            st.markdown(f"- {item}")

    langs = metrics.get("languages") or []
    if langs:
        st.markdown("#### Languages")
        st.markdown(" | ".join(langs[:8]))

    top_repos = data.get("top_repos") or []
    if top_repos:
        st.markdown("#### Proof points")
        for repo in top_repos:
            st.markdown(
                f"""
                <div class="repo-card">
                    <div>
                        <a href="{repo['url']}" target="_blank">{repo['name']}</a>
                        <div class="repo-meta">{repo['language']} - {repo['stars']} stars - {repo['forks']} forks</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def _metric_card(value, label):
    return f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
    </div>
    """
