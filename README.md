# CampusConnect


Built for the UnsaidTalks AICore Connect Hackathon.

## Stack
- **Frontend + Backend:** Python + Streamlit
- **Database:** SQLite (zero config, file-based)

## Setup & Run

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the app
streamlit run app.py
```

App will open at → http://localhost:8501

---

## Demo Login Credentials (password: `demo123`)

| Role | Email |
|------|-------|
| Organization | org@demo.com |
| Ambassador | arjun@demo.com |
| Ambassador | priya@demo.com |
| Ambassador | rahul@demo.com |

---

## Features

### For Organizations
- ✅ Create & manage tasks (referral, promotion, content, event)
- ✅ View all ambassadors and their performance
- ✅ Review and approve/reject submissions with scoring
- ✅ Real-time leaderboard
- ✅ Dashboard with key metrics
- ✅ Unique invite code for ambassador onboarding

### For Ambassadors
- ✅ View and submit assigned tasks with proof
- ✅ Track points, streaks, and submission status
- ✅ Earn badges automatically (First Step, Champion, On Fire, etc.)
- ✅ View leaderboard ranking among peers

---

## File Structure
```
campusconnect/
├── app.py          # Main Streamlit app (all UI + routing)
├── database.py     # SQLite schema + seed data
├── helpers.py      # Business logic & DB queries
├── requirements.txt
└── README.md
```

## How Scoring Works
- Each task has a point value set by the org
- Reviewers can award 0–max points per submission
- Points trigger automatic badge unlocks
- Leaderboard sorts by total points in real-time
