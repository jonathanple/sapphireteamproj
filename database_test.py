# sqlite_db.py
import sqlite3
from datetime import datetime
import os

# Absolute path to ensure consistent DB file
DB_PATH = os.path.join(os.path.dirname(__file__), "hr_input_summaries.db")

#create the table in the database
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create a table for summaries if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS hr_input_summaries (
            store_id INTEGER PRIMARY KEY AUTOINCREMENT,
            summary TEXT,
            employee_id TEXT,
            input_date TEXT
        )
    ''')

    conn.commit()
    conn.close()


def save_to_sqlite(summary, employee_ID, input_date=None):
    if input_date is None:
        input_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO hr_input_summaries (summary, employee_ID, input_date)
        VALUES (?, ?, ?)
    ''', (summary, employee_ID, input_date))
    
    conn.commit()
    conn.close()

def get_all_summaries():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM hr_input_summaries")
    rows = cursor.fetchall()

    conn.close()
    return rows



# Step 1: Initialize the database (run once)
init_db()

# Step 2: Save a test record (optional: you can skip the date)
save_to_sqlite('Employee asked about time off policy.', 'EMP123', '2025-04-12 22:15:30')

# Step 3: Retrieve and print all summaries
rows = get_all_summaries()
for row in rows:
    print(row)
