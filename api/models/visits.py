import sqlite3

# Initialize in-memory database
conn = sqlite3.connect(':memory:', check_same_thread=False)
cursor = conn.cursor()

# Create visits table
cursor.execute('''
CREATE TABLE visits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    content TEXT NOT NULL,
    title TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')
conn.commit()

def get_visits():
    cursor.execute('SELECT * FROM visits')
    rows = cursor.fetchall()
    return [{'id': row[0], 'url': row[1], 'content': row[2], 'title': row[3], 'timestamp': row[4]} for row in rows]

def add_visit(url, content, title, timestamp):
    cursor.execute('INSERT INTO visits (url, content, title, timestamp) VALUES (?, ?, ?, ?)', (url, content, title, timestamp))
    conn.commit()
    return {'id': cursor.lastrowid, 'url': url, 'content': content, 'title': title, 'timestamp': timestamp}