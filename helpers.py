from database import get_conn, hash_password

def login_user(email, password):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password=?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def register_org(name, email, password, org_name, org_desc):
    conn = get_conn()
    c = conn.cursor()
    import random, string
    invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    try:
        c.execute("INSERT INTO users (name, email, password, role) VALUES (?,?,?,'org')",
                  (name, email, hash_password(password)))
        user_id = c.lastrowid
        c.execute("INSERT INTO organizations (name, description, owner_id, invite_code) VALUES (?,?,?,?)",
                  (org_name, org_desc, user_id, invite_code))
        org_id = c.lastrowid
        c.execute("UPDATE users SET org_id=? WHERE id=?", (org_id, user_id))
        conn.commit()
        return True, "Account created! Login now."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def register_ambassador(name, email, password, college, invite_code, github_username=None):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("SELECT id FROM organizations WHERE invite_code=?", (invite_code,))
        org = c.fetchone()
        if not org:
            return False, "Invalid invite code."
        org_id = org['id']
        c.execute("""INSERT INTO users (name, email, password, role, college, org_id, github_username)
                     VALUES (?,?,?,'ambassador',?,?,?)""",
                  (name, email, hash_password(password), college, org_id, (github_username or "").strip() or None))
        amb_id = c.lastrowid
        c.execute("INSERT INTO ambassador_orgs (ambassador_id, org_id) VALUES (?,?)", (amb_id, org_id))
        conn.commit()
        return True, "Joined successfully! Login now."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_org(org_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM organizations WHERE id=?", (org_id,))
    org = c.fetchone()
    conn.close()
    return dict(org) if org else None

def get_user(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    conn.close()
    return dict(user) if user else None

def get_ambassadors(org_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT u.*, 
                 (SELECT COUNT(*) FROM submissions s 
                  JOIN tasks t ON s.task_id=t.id 
                  WHERE s.ambassador_id=u.id AND s.status='approved' AND t.org_id=?) as tasks_done
                 FROM users u 
                 WHERE u.org_id=? AND u.role='ambassador'
                 ORDER BY u.points DESC""", (org_id, org_id))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ambassadors_with_github(org_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT u.*,
                 ap.status as pipeline_status,
                 ap.notes as pipeline_notes,
                 ap.updated_at as pipeline_updated_at,
                 (SELECT COUNT(*) FROM submissions s
                  JOIN tasks t ON s.task_id=t.id
                  WHERE s.ambassador_id=u.id AND s.status='approved' AND t.org_id=?) as tasks_done
                 FROM users u
                 LEFT JOIN ambassador_pipeline ap
                   ON ap.ambassador_id=u.id AND ap.org_id=?
                 WHERE u.org_id=? AND u.role='ambassador'
                 ORDER BY
                    CASE WHEN u.github_score IS NULL THEN -1 ELSE u.github_score END DESC,
                    u.points DESC,
                    u.name ASC""", (org_id, org_id, org_id))
    rows = c.fetchall()
    conn.close()
    ambassadors = [dict(r) for r in rows]
    for ambassador in ambassadors:
        ambassador["pipeline_status"] = ambassador.get("pipeline_status") or "watch"
        ambassador["fit_score"] = calculate_fit_score(ambassador)
        ambassador["fit_label"] = fit_label(ambassador["fit_score"])
    return ambassadors

def get_tasks(org_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT t.*, 
                 COUNT(DISTINCT s.id) as total_submissions,
                 SUM(CASE WHEN s.status='approved' THEN 1 ELSE 0 END) as approved_count,
                 SUM(CASE WHEN s.status='pending' THEN 1 ELSE 0 END) as pending_count
                 FROM tasks t
                 LEFT JOIN submissions s ON s.task_id=t.id
                 WHERE t.org_id=?
                 GROUP BY t.id
                 ORDER BY t.created_at DESC""", (org_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_ambassador_tasks(ambassador_id, org_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT t.*,
                 s.id as sub_id, s.status as sub_status, s.score as sub_score, s.feedback
                 FROM tasks t
                 LEFT JOIN submissions s ON s.task_id=t.id AND s.ambassador_id=?
                 WHERE t.org_id=? AND t.status='active'
                 ORDER BY t.created_at DESC""", (ambassador_id, org_id))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def submit_task(task_id, ambassador_id, proof_text, proof_link):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO submissions (task_id, ambassador_id, proof_text, proof_link)
                     VALUES (?,?,?,?)""", (task_id, ambassador_id, proof_text, proof_link))
        conn.commit()
        return True, "Submitted successfully!"
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()

def get_pending_submissions(org_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT s.*, t.title as task_title, t.points_reward, u.name as ambassador_name, u.college
                 FROM submissions s
                 JOIN tasks t ON s.task_id=t.id
                 JOIN users u ON s.ambassador_id=u.id
                 WHERE t.org_id=? AND s.status='pending'
                 ORDER BY s.submitted_at DESC""", (org_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def review_submission(sub_id, status, score, feedback, ambassador_id, points_reward):
    conn = get_conn()
    c = conn.cursor()
    try:
        c.execute("""UPDATE submissions SET status=?, score=?, feedback=?, reviewed_at=CURRENT_TIMESTAMP
                     WHERE id=?""", (status, score, feedback, sub_id))
        if status == 'approved':
            c.execute("UPDATE users SET points=points+?, last_active=DATE('now') WHERE id=?",
                      (points_reward, ambassador_id))
            check_and_award_badges(c, ambassador_id)
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def check_and_award_badges(c, user_id):
    c.execute("SELECT points FROM users WHERE id=?", (user_id,))
    user = c.fetchone()
    if not user:
        return

    c.execute("""SELECT COUNT(*) as cnt FROM submissions 
                 WHERE ambassador_id=? AND status='approved'""", (user_id,))
    tasks_done = c.fetchone()['cnt']

    c.execute("SELECT * FROM badges")
    badges = c.fetchall()
    for badge in badges:
        val = badge['condition_value']
        ctype = badge['condition_type']
        earned = False
        if ctype == 'tasks_completed' and tasks_done >= val:
            earned = True
        elif ctype == 'points' and user['points'] >= val:
            earned = True
        if earned:
            try:
                c.execute("INSERT OR IGNORE INTO user_badges (user_id, badge_id) VALUES (?,?)",
                          (user_id, badge['id']))
            except:
                pass

def get_user_badges(user_id):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""SELECT b.* FROM badges b
                 JOIN user_badges ub ON b.id=ub.badge_id
                 WHERE ub.user_id=?""", (user_id,))
    rows = c.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def save_github_data(user_id, github_username, github_score, github_tier, github_data):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""UPDATE users
                 SET github_username=?,
                     github_score=?,
                     github_tier=?,
                     github_data=?
                 WHERE id=?""", (github_username, github_score, github_tier, github_data, user_id))
    conn.commit()
    conn.close()

def create_task(org_id, title, desc, task_type, points, deadline):
    conn = get_conn()
    c = conn.cursor()
    c.execute("""INSERT INTO tasks (org_id, title, description, task_type, points_reward, deadline)
                 VALUES (?,?,?,?,?,?)""", (org_id, title, desc, task_type, points, str(deadline)))
    conn.commit()
    conn.close()

def get_org_stats(org_id):
    conn = get_conn()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT COUNT(*) as cnt FROM users WHERE org_id=? AND role='ambassador'", (org_id,))
    stats['total_ambassadors'] = c.fetchone()['cnt']
    c.execute("SELECT COUNT(*) as cnt FROM tasks WHERE org_id=?", (org_id,))
    stats['total_tasks'] = c.fetchone()['cnt']
    c.execute("""SELECT COUNT(*) as cnt FROM submissions s 
                 JOIN tasks t ON s.task_id=t.id WHERE t.org_id=? AND s.status='approved'""", (org_id,))
    stats['approved_submissions'] = c.fetchone()['cnt']
    c.execute("""SELECT COUNT(*) as cnt FROM submissions s 
                 JOIN tasks t ON s.task_id=t.id WHERE t.org_id=? AND s.status='pending'""", (org_id,))
    stats['pending_review'] = c.fetchone()['cnt']
    c.execute("""SELECT COUNT(*) as cnt FROM users
                 WHERE org_id=? AND role='ambassador' AND github_username IS NOT NULL
                 AND TRIM(github_username) != ''""", (org_id,))
    stats['github_linked'] = c.fetchone()['cnt']
    c.execute("""SELECT COUNT(*) as cnt FROM ambassador_pipeline
                 WHERE org_id=? AND status='shortlist'""", (org_id,))
    stats['shortlisted'] = c.fetchone()['cnt']
    c.execute("""SELECT COUNT(*) as cnt FROM ambassador_pipeline
                 WHERE org_id=? AND status='high_potential'""", (org_id,))
    stats['high_potential'] = c.fetchone()['cnt']
    conn.close()
    return stats

def get_ambassador_stats(user_id, org_id):
    conn = get_conn()
    c = conn.cursor()
    stats = {}
    c.execute("SELECT points, streak FROM users WHERE id=?", (user_id,))
    u = c.fetchone()
    stats['points'] = u['points']
    stats['streak'] = u['streak']
    c.execute("""SELECT COUNT(*) as cnt FROM submissions s
                 JOIN tasks t ON s.task_id=t.id
                 WHERE s.ambassador_id=? AND s.status='approved' AND t.org_id=?""", (user_id, org_id))
    stats['tasks_done'] = c.fetchone()['cnt']
    c.execute("""SELECT COUNT(*) as cnt FROM submissions s
                 JOIN tasks t ON s.task_id=t.id
                 WHERE s.ambassador_id=? AND s.status='pending' AND t.org_id=?""", (user_id, org_id))
    stats['pending'] = c.fetchone()['cnt']
    conn.close()
    return stats

def calculate_fit_score(ambassador):
    github_score = ambassador.get("github_score") or 0
    points = ambassador.get("points") or 0
    tasks_done = ambassador.get("tasks_done") or 0
    streak = ambassador.get("streak") or 0

    delivery_score = min(35, points // 12)
    execution_score = min(25, tasks_done * 4)
    consistency_score = min(15, streak * 3)
    technical_score = min(25, int(github_score * 0.25))
    return min(100, delivery_score + execution_score + consistency_score + technical_score)

def fit_label(score):
    if score >= 80:
        return "High potential"
    if score >= 65:
        return "Shortlist ready"
    if score >= 45:
        return "Worth tracking"
    return "Early signal"

def save_pipeline_status(org_id, ambassador_id, status, notes=""):
    conn = get_conn()
    c = conn.cursor()
    c.execute(
        """INSERT INTO ambassador_pipeline (org_id, ambassador_id, status, notes, updated_at)
           VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
           ON CONFLICT(org_id, ambassador_id)
           DO UPDATE SET status=excluded.status,
                         notes=excluded.notes,
                         updated_at=CURRENT_TIMESTAMP""",
        (org_id, ambassador_id, status, notes),
    )
    conn.commit()
    conn.close()

def get_shortlist_board(org_id):
    ambassadors = get_ambassadors_with_github(org_id)
    board = {"watch": [], "shortlist": [], "high_potential": []}
    for ambassador in ambassadors:
        board[ambassador.get("pipeline_status") or "watch"].append(ambassador)
    return board
