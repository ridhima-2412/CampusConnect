import sqlite3
import hashlib
import random

DB_PATH = "campusconnect.db"

def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_db():
    conn = get_conn()
    c = conn.cursor()

    c.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('org', 'ambassador')),
        college TEXT,
        org_id INTEGER,
        points INTEGER DEFAULT 0,
        streak INTEGER DEFAULT 0,
        last_active DATE,
        avatar_color TEXT DEFAULT '#6366f1',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        owner_id INTEGER,
        invite_code TEXT UNIQUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        org_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        description TEXT,
        task_type TEXT CHECK(task_type IN ('referral', 'promotion', 'content', 'event', 'other')),
        points_reward INTEGER DEFAULT 10,
        deadline DATE,
        status TEXT DEFAULT 'active' CHECK(status IN ('active', 'closed')),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(org_id) REFERENCES organizations(id)
    );

    CREATE TABLE IF NOT EXISTS submissions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_id INTEGER NOT NULL,
        ambassador_id INTEGER NOT NULL,
        proof_text TEXT,
        proof_link TEXT,
        status TEXT DEFAULT 'pending' CHECK(status IN ('pending', 'approved', 'rejected')),
        score INTEGER DEFAULT 0,
        feedback TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        FOREIGN KEY(task_id) REFERENCES tasks(id),
        FOREIGN KEY(ambassador_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS badges (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        icon TEXT,
        condition_type TEXT,
        condition_value INTEGER
    );

    CREATE TABLE IF NOT EXISTS user_badges (
        user_id INTEGER,
        badge_id INTEGER,
        earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(user_id, badge_id)
    );

    CREATE TABLE IF NOT EXISTS ambassador_orgs (
        ambassador_id INTEGER,
        org_id INTEGER,
        joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(ambassador_id, org_id)
    );

    CREATE TABLE IF NOT EXISTS ambassador_pipeline (
        org_id INTEGER NOT NULL,
        ambassador_id INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'watch' CHECK(status IN ('watch', 'shortlist', 'high_potential')),
        notes TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(org_id, ambassador_id)
    );
    """)

    ensure_user_github_columns(c)

    c.execute("SELECT COUNT(*) FROM badges")
    if c.fetchone()[0] == 0:
        badges = [
            ("First Step", "Complete your first task", "🎯", "tasks_completed", 1),
            ("Go-Getter", "Complete 5 tasks", "🚀", "tasks_completed", 5),
            ("Champion", "Complete 10 tasks", "🏆", "tasks_completed", 10),
            ("Point Hustler", "Earn 100 points", "💰", "points", 100),
            ("High Roller", "Earn 500 points", "💎", "points", 500),
            ("On Fire", "Maintain 7-day streak", "🔥", "streak", 7),
            ("Consistent", "Maintain 3-day streak", "⚡", "streak", 3),
        ]
        c.executemany("INSERT INTO badges (name, description, icon, condition_type, condition_value) VALUES (?,?,?,?,?)", badges)

    c.execute("SELECT COUNT(*) FROM users")
    if c.fetchone()[0] == 0:
        seed_demo_data(c)
    seed_demo_github_links(c)
    ensure_demo_login_accounts(c)

    conn.commit()
    conn.close()

def ensure_user_github_columns(c):
    c.execute("PRAGMA table_info(users)")
    existing_columns = {row["name"] for row in c.fetchall()}

    github_columns = {
        "github_username": "TEXT",
        "github_score": "INTEGER DEFAULT 0",
        "github_tier": "TEXT",
        "github_data": "TEXT",
    }

    for column, definition in github_columns.items():
        if column not in existing_columns:
            c.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")

def seed_demo_data(c):
    colors = ['#6366f1', '#ec4899', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6']

    c.execute("""INSERT INTO users (name, email, password, role, avatar_color)
                 VALUES (?, ?, ?, 'org', ?)""",
              ("TechCorp HQ", "org@demo.com", hash_password("demo123"), '#6366f1'))
    org_user_id = c.lastrowid

    c.execute("""INSERT INTO organizations (name, description, owner_id, invite_code)
                 VALUES (?, ?, ?, ?)""",
              ("TechCorp", "Leading tech startup building the future", org_user_id, "TECHCORP2024"))
    org_id = c.lastrowid

    c.execute("UPDATE users SET org_id=? WHERE id=?", (org_id, org_user_id))

    ambassadors = [
        ("Arjun Sharma", "arjun@demo.com", "IIT Delhi", 340, 5),
        ("Priya Patel", "priya@demo.com", "BITS Pilani", 290, 3),
        ("Rahul Gupta", "rahul@demo.com", "NIT Trichy", 210, 7),
        ("Sneha Nair", "sneha@demo.com", "VIT Vellore", 180, 2),
        ("Karan Singh", "karan@demo.com", "DTU Delhi", 95, 1),
    ]

    amb_ids = []
    for i, (name, email, college, points, streak) in enumerate(ambassadors):
        c.execute("""INSERT INTO users (name, email, password, role, college, org_id, points, streak, avatar_color)
                     VALUES (?, ?, ?, 'ambassador', ?, ?, ?, ?, ?)""",
                  (name, email, hash_password("demo123"), college, org_id, points, streak, colors[i % len(colors)]))
        amb_ids.append(c.lastrowid)
        c.execute("INSERT INTO ambassador_orgs (ambassador_id, org_id) VALUES (?,?)", (c.lastrowid, org_id))

    tasks = [
        ("Instagram Story Campaign", "Post a story about our product with the hashtag #TechCorpRises", "promotion", 50, "2024-12-31"),
        ("College Referral Drive", "Get 3 friends to sign up using your referral code", "referral", 80, "2024-12-25"),
        ("LinkedIn Article", "Write a 500-word article about campus innovation and tag us", "content", 60, "2024-12-28"),
        ("Campus Event Hosting", "Organize a 20-person meetup at your college", "event", 120, "2024-12-30"),
        ("Product Review Video", "Create a 60-second reel reviewing our product", "content", 70, "2024-12-27"),
    ]

    task_ids = []
    for title, desc, ttype, pts, deadline in tasks:
        c.execute("""INSERT INTO tasks (org_id, title, description, task_type, points_reward, deadline)
                     VALUES (?,?,?,?,?,?)""", (org_id, title, desc, ttype, pts, deadline))
        task_ids.append(c.lastrowid)

    statuses = ['approved', 'approved', 'pending', 'rejected', 'pending']
    for i, amb_id in enumerate(amb_ids[:4]):
        for j, task_id in enumerate(task_ids[:3]):
            status = statuses[(i + j) % len(statuses)]
            score = random.randint(40, 100) if status == 'approved' else 0
            c.execute("""INSERT INTO submissions (task_id, ambassador_id, proof_text, proof_link, status, score)
                         VALUES (?,?,?,?,?,?)""",
                      (task_id, amb_id, f"Completed task: uploaded proof and evidence",
                       "https://example.com/proof", status, score))

    c.execute("SELECT id FROM badges WHERE condition_type='tasks_completed' AND condition_value=1")
    badge = c.fetchone()
    if badge:
        for amb_id in amb_ids[:3]:
            try:
                c.execute("INSERT INTO user_badges (user_id, badge_id) VALUES (?,?)", (amb_id, badge['id']))
            except:
                pass

def seed_demo_github_links(c):
    demo_profiles = {
        "arjun@demo.com": "octocat",
        "priya@demo.com": "gaearon",
        "rahul@demo.com": "sindresorhus",
    }
    for email, username in demo_profiles.items():
        c.execute("""UPDATE users
                     SET github_username=COALESCE(NULLIF(github_username, ''), ?)
                     WHERE email=?""", (username, email))

def ensure_demo_login_accounts(c):
    demo_accounts = [
        "org@demo.com",
        "arjun@demo.com",
        "priya@demo.com",
        "rahul@demo.com",
        "sneha@demo.com",
        "karan@demo.com",
    ]
    demo_hash = hash_password("demo123")
    for email in demo_accounts:
        c.execute("UPDATE users SET password=? WHERE email=?", (demo_hash, email))
