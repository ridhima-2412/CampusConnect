#  CampusConnect

CampusConnect is a centralized platform to manage Campus Ambassador programs with **task automation, performance tracking, and gamification**, enhanced by a **GitHub intelligence layer** for fast talent evaluation.

---
## 🔗 Live Demo

[Open CampusConnect Live Demo](https://ridhima-2412-campusconnect-app-yxr7oo.streamlit.app/)

## 🎥 Demo Video

[Watch Demo Video](https://drive.google.com/open?id=1leOYtpEm47kVqAUYMg2AiLzUeHGwl83Z)


This demo showcases:
- Admin dashboard and insights
- Task assignment and submission workflow
- Leaderboard and gamification system
- GitHub-based ambassador evaluation

---

## 💡 Problem

Campus Ambassador programs are often managed using spreadsheets, forms, and messaging apps, leading to:

- ❌ No centralized system  
- ❌ Unclear task management  
- ❌ No motivation or recognition  
- ❌ No way to identify top performers  

This results in low engagement and poor scalability.

---

## 🚀 Solution

CampusConnect transforms this into a **structured, scalable, and engaging system** by:

- Automating task assignment and tracking  
- Introducing gamification (leaderboards, scores, recognition)  
- Providing real-time dashboards  
- Using GitHub intelligence to evaluate technical potential  

---

## ⚙️ Key Features

### 👩‍💼 Organization Panel
- Dashboard with real-time insights  
- Task creation and submission review  
- Ambassador performance tracking  
- Leaderboard and engagement metrics  
- Shortlist Board (Watch / High Potential / Selected)  
- GitHub Lab for analyzing public profiles  

### 🧑‍🎓 Ambassador Panel
- View and complete assigned tasks  
- Submit proof of work  
- Track personal performance and progress  
- View leaderboard ranking  
- GitHub profile analysis  

---

## 🧠 Smart Insights (Innovation)

- **GitHub Analyzer** generates:
  - Score (out of 100)
  - Strengths & risks
  - Role hints
  - Repository proof points  

- **Ambassador Fit Score** combines:
  - Task completion
  - Consistency (streaks)
  - GitHub score  

👉 Enables fast, data-driven decision making.

---

## 🛠 Tech Stack

- **Frontend:** Streamlit  
- **Backend:** Python  
- **Database:** SQLite  
- **Architecture:** Modular (separate pages, components, and services)

---

## 📂 Project Structure





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

## Impact
Reduces manual effort in managing ambassadors
Improves engagement through gamification
Helps identify top performers instantly
Bridges operations + talent discovery

 ## Conclusion

CampusConnect converts a fragmented, manual process into a data-driven, gamified, and scalable growth engine for organizations.3` on startup.
- A GitHub token is optional but recommended during live demos to avoid rate limits.
