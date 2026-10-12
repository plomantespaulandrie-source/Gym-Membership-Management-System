import sqlite3
import calendar
from datetime import datetime, date, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'gym_management.db')

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS members (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            member_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            contact_number TEXT NOT NULL,
            membership_plan TEXT NOT NULL,
            start_date TEXT NOT NULL,
            expiration_date TEXT NOT NULL,
            payment_status TEXT NOT NULL,
            amount_paid REAL DEFAULT 0.0,
            last_payment_date TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def calculate_expiration_date(start_date, plan):
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    
    if plan == "Monthly":
        month_sum = start_date.month + 1
    elif plan == "3 Months":
        month_sum = start_date.month + 3
    elif plan == "6 Months":
        month_sum = start_date.month + 6
    elif plan == "1 Year":
        month_sum = start_date.month + 12
    else:
        return start_date + timedelta(days=30)
    
    year = start_date.year + ((month_sum - 1) // 12)
    month = ((month_sum - 1) % 12) + 1
    max_days = calendar.monthrange(year, month)[1]
    day = min(start_date.day, max_days)
    return date(year, month, day)

def get_membership_status(expiration_date_str):
    if not expiration_date_str:
        return "Expired"
    exp_date = datetime.strptime(expiration_date_str, "%Y-%m-%d").date()
    today = date.today()
    return "Active" if exp_date >= today else "Expired"

def generate_next_member_id():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT member_id FROM members ORDER BY id DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    
    if row and row['member_id'].startswith('GYM-'):
        try:
            last_num = int(row['member_id'].split('-')[1])
            return f"GYM-{last_num + 1:04d}"
        except ValueError:
            pass
    return "GYM-1001"

def format_member(row):
    if not row:
        return None
    d = dict(row)
    d['membership_status'] = get_membership_status(d['expiration_date'])
    return d

def add_member(full_name, age, contact_number, membership_plan, start_date_str, payment_status, amount_paid=0.0):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
    exp_date = calculate_expiration_date(start_date, membership_plan)
    exp_date_str = exp_date.strftime("%Y-%m-%d")
    
    member_id = generate_next_member_id()
    last_payment = start_date_str if payment_status == "Paid" else None
    
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO members (
            member_id, full_name, age, contact_number, membership_plan,
            start_date, expiration_date, payment_status, amount_paid, last_payment_date
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (member_id, full_name, age, contact_number, membership_plan,
          start_date_str, exp_date_str, payment_status, amount_paid, last_payment))
    
    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return get_member_by_db_id(new_id)

def get_all_members():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [format_member(row) for row in rows]

def get_member_by_db_id(db_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE id = ?", (db_id,))
    row = cursor.fetchone()
    conn.close()
    return format_member(row)

def get_member_by_member_id(member_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM members WHERE LOWER(member_id) = LOWER(?)", (member_id.strip(),))
    row = cursor.fetchone()
    conn.close()
    return format_member(row)

def search_members(query):
    if not query:
        return get_all_members()
    query_clean = f"%{query.strip()}%"
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM members 
        WHERE LOWER(member_id) LIKE LOWER(?) OR LOWER(full_name) LIKE LOWER(?) OR contact_number LIKE ?
        ORDER BY id DESC
    ''', (query_clean, query_clean, query_clean))
    rows = cursor.fetchall()
    conn.close()
    return [format_member(row) for row in rows]

def update_member(db_id, full_name, age, contact_number, membership_plan, start_date_str, expiration_date_str, payment_status, amount_paid):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE members SET
            full_name = ?,
            age = ?,
            contact_number = ?,
            membership_plan = ?,
            start_date = ?,
            expiration_date = ?,
            payment_status = ?,
            amount_paid = ?
        WHERE id = ?
    ''', (full_name, age, contact_number, membership_plan, start_date_str, expiration_date_str, payment_status, amount_paid, db_id))
    conn.commit()
    conn.close()
    return get_member_by_db_id(db_id)

def delete_member(db_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM members WHERE id = ?", (db_id,))
    deleted_count = cursor.rowcount
    conn.commit()
    conn.close()
    return deleted_count > 0

def record_payment(db_id, amount_paid, payment_status, payment_date_str, extend_plan=None):
    member = get_member_by_db_id(db_id)
    if not member:
        return None
    
    total_paid = float(member['amount_paid'] or 0.0) + float(amount_paid)
    new_exp_date_str = member['expiration_date']
    
    if extend_plan:
        current_exp = datetime.strptime(member['expiration_date'], "%Y-%m-%d").date()
        today = date.today()
        base_date = current_exp if current_exp >= today else today
        new_exp_date = calculate_expiration_date(base_date, extend_plan)
        new_exp_date_str = new_exp_date.strftime("%Y-%m-%d")
        new_plan = extend_plan
    else:
        new_plan = member['membership_plan']

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE members SET
            payment_status = ?,
            amount_paid = ?,
            last_payment_date = ?,
            expiration_date = ?,
            membership_plan = ?
        WHERE id = ?
    ''', (payment_status, total_paid, payment_date_str, new_exp_date_str, new_plan, db_id))
    conn.commit()
    conn.close()
    return get_member_by_db_id(db_id)

def get_dashboard_stats():
    members = get_all_members()
    total = len(members)
    active = sum(1 for m in members if m['membership_status'] == 'Active')
    expired = sum(1 for m in members if m['membership_status'] == 'Expired')
    pending_payment = sum(1 for m in members if m['payment_status'] in ['Pending', 'Overdue'])
    total_revenue = sum(m['amount_paid'] for m in members)
    
    return {
        'total': total,
        'active': active,
        'expired': expired,
        'pending_payment': pending_payment,
        'total_revenue': total_revenue
    }
