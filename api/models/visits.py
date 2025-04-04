import sqlite3
import os

# Ensure the data directory exists
os.makedirs('data', exist_ok=True)

# Connect to the database in the data directory
conn = sqlite3.connect('data/visits.db', check_same_thread=False)
cursor = conn.cursor()

# Add the 'rating' column if it doesn't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    report TEXT NOT NULL,
    title TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    rating INTEGER DEFAULT -1
)
''')
conn.commit()

def get_visits():
    cursor.execute('SELECT id, url, title, timestamp, rating FROM visits')
    rows = cursor.fetchall()
    return [{'id': row[0], 'url': row[1], 'title': row[2], 'timestamp': row[3], 'rating': row[4]} for row in rows]

def get_visits_for_report():
    cursor.execute('SELECT * FROM visits')
    rows = cursor.fetchall()
    return [{'id': row[0], 'url': row[1], 'report': row[2], 'title': row[3], 'timestamp': row[4], 'rating': row[5]} for row in rows]

def add_visit(url, report, title, timestamp, rating):
    try:
        cursor.execute('INSERT INTO visits (url, report, title, timestamp, rating) VALUES (?, ?, ?, ?, ?)', (url, report, title, timestamp, rating))
        conn.commit()
        return {'id': cursor.lastrowid, 'url': url, 'report': report, 'title': title, 'timestamp': timestamp, 'rating': rating}
    except sqlite3.IntegrityError:
        cursor.execute('SELECT * FROM visits WHERE url = ?', (url,))
        row = cursor.fetchone()
        return {'id': row[0], 'url': row[1], 'report': row[2], 'title': row[3], 'timestamp': row[4], 'rating': row[5]}

def get_visit_by_url(url):
    cursor.execute('SELECT * FROM visits WHERE url = ?', (url,))
    row = cursor.fetchone()
    if row:
        return {'id': row[0], 'url': row[1], 'report': row[2], 'title': row[3], 'timestamp': row[4], 'rating': row[5]}
    return None

def clear_visits():
    cursor.execute('DELETE FROM visits')
    conn.commit()