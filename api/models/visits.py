import sqlite3

# Initialize in-memory database
conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()

# Create visits table with URL as a unique key
cursor.execute('''
CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL UNIQUE,
    content TEXT NOT NULL,
    title TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')
conn.commit()

def get_visits():
    cursor.execute('SELECT id, url, title, timestamp FROM visits')
    rows = cursor.fetchall()
    return [{'id': row[0], 'url': row[1], 'title': row[2], 'timestamp': row[3]} for row in rows]

def get_visits_for_report():
    cursor.execute('SELECT * FROM visits')
    rows = cursor.fetchall()
    return [{'id': row[0], 'url': row[1], 'content': row[2], 'title': row[3], 'timestamp': row[4]} for row in rows]

def add_visit(url, content, title, timestamp):
    try:
        cursor.execute('INSERT INTO visits (url, content, title, timestamp) VALUES (?, ?, ?, ?)', (url, content, title, timestamp))
        conn.commit()
        return {'id': cursor.lastrowid, 'url': url, 'content': content, 'title': title, 'timestamp': timestamp}
    except sqlite3.IntegrityError:
        return {'error': 'URL already exists in the database'}
    
def clear_visits():
    cursor.execute('DELETE FROM visits')
    conn.commit()