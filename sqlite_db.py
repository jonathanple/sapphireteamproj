import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("hr_conversations.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conversation_summaries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id TEXT,
            employee_name TEXT,
            question TEXT,
            answer TEXT,
            summary TEXT,
            date_asked TEXT
        )
    ''')

    conn.commit()
    conn.close()

def save_to_sqlite(employee_id, employee_name, question, answer, summary):
    conn = sqlite3.connect("hr_conversations.db")
    cursor = conn.cursor()

    date_asked = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute('''
        INSERT INTO conversation_summaries (employee_id, employee_name, question, answer, summary, date_asked)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (employee_id, employee_name, question, answer, summary, date_asked))

    conn.commit()
    conn.close()

def get_all_summaries():
    conn = sqlite3.connect("hr_conversations.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM conversation_summaries")
    rows = cursor.fetchall()

    conn.close()
    return rows
