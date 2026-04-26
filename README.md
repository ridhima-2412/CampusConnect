# CampusConnect

CampusConnect is a Streamlit app for managing campus ambassador programs with a built-in GitHub intelligence layer. It helps organizations create tasks, review submissions, compare ambassadors, and turn public GitHub signals into shortlist decisions in under two minutes.

## What problem it solves

Most campus ambassador workflows track activity, but they do not help organizations understand technical potential quickly. CampusConnect combines:

- ambassador execution data
- public GitHub signal analysis
- shortlist workflow
- lightweight review and scoring

That makes the product useful for both operations and talent discovery.

## Why this project is strong against the judging criteria

### Impact

- One GitHub username gives a structured signal snapshot with score, verdict, strengths, risks, and proof-point repositories.
- Organizations can compare ambassadors without asking the user to do heavy manual work.

### Innovation

- GitHub is not treated like a decorative badge.
- The product connects GitHub analysis to real ambassador operations through Fit Score and a Shortlist Board.

### Technical execution

- Streamlit frontend
- SQLite backend
- modular structure with separated pages, theme, and shared components
- seeded demo data and deterministic demo logins

### User experience

- dark-themed dashboard layout
- separate organization and ambassador flows
- fast GitHub analysis flow
- shortlist-ready decision surfaces

### Presentation

- easy live demo path
- clear before-and-after story
- immediate visible output from GitHub Lab and Fit Score

## Core features

### Organization features

- overview dashboard with operational insights
- task creation and review queue
- ambassador roster with GitHub and Fit Score signals
- GitHub Lab for analyzing any public profile
- Shortlist Board with `Watch`, `Shortlist`, and `High Potential` lanes
- leaderboard and program health summaries

### Ambassador features

- task submission and review tracking
- badge progress and personal dashboard
- GitHub profile analysis and save flow
- visibility improvements through public technical signal

## GitHub analysis model

The GitHub analyzer scores public signals using:

- profile completeness
- original repositories
- recent activity
- reach and engagement
- language breadth

It returns:

- overall score out of 100
- tier
- role hint
- verdict
- strengths
- watch-outs
- repository proof points

## Fit Score

CampusConnect also generates an internal `Ambassador Fit Score` using:

- delivery points
- approved task count
- streak consistency
- GitHub score

This helps organizations move from raw data to action faster.

## Project structure

```text
CampusConnect/
|-- app.py
|-- auth_page.py
|-- org_pages.py
|-- ambassador_pages.py
|-- ui_theme.py
|-- ui_components.py
|-- github_analyzer.py
|-- helpers.py
|-- database.py
|-- requirements.txt
|-- README.md
|-- DEMO_SCRIPT.md
```

## Run locally

1. Install dependencies

```bash
pip install -r requirements.txt
```

2. Start the app

```bash
streamlit run app.py
```

3. Open the URL shown by Streamlit, usually:

```text
http://localhost:8501
```

## Demo accounts

Password for all demo accounts:

```text
demo123
```

| Role | Email |
|------|-------|
| Organization | org@demo.com |
| Ambassador | arjun@demo.com |
| Ambassador | priya@demo.com |
| Ambassador | rahul@demo.com |

## Best demo path

1. Start on the landing page and explain the promise: fast GitHub assessment for ambassador programs.
2. Log in as the organization.
3. Show the overview dashboard and shortlist counts.
4. Open GitHub Lab and analyze a public GitHub profile.
5. Open Ambassadors to show GitHub score, Fit Score, and pipeline actions.
6. Open Shortlist Board to show decision lanes.
7. Switch to an ambassador account and show task progress and personal GitHub score.

## Notes

- The app seeds demo data automatically.
- Demo account passwords are reset to `demo123` on startup.
- A GitHub token is optional but recommended during live demos to avoid rate limits.
