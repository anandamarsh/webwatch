import sqlite3
import threading
import time
import os
from api.config import Config
from api import logger

def get_db_connection():
    """Get a database connection with row factory"""
    conn = sqlite3.connect(Config.DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables"""
    logger.info(f"Initializing database at {Config.DB_PATH}")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create content_store table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS content_store (
        hash TEXT PRIMARY KEY,
        content TEXT NOT NULL,
        metadata TEXT
    )
    ''')
    
    # Check if visits table exists
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='visits'")
    visits_exists = cursor.fetchone() is not None
    
    if visits_exists:
        # If visits table exists, check if links column exists
        cursor.execute("PRAGMA table_info(visits)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add links column if it doesn't exist
        if 'links' not in columns:
            logger.info("Adding links column to visits table")
            cursor.execute("ALTER TABLE visits ADD COLUMN links TEXT")
        
        # Check if URL is the primary key
        cursor.execute("PRAGMA table_info(visits)")
        columns = cursor.fetchall()
        
        # Check if URL is the primary key
        url_is_primary = False
        for col in columns:
            if col[1] == 'url' and col[5] == 1:  # col[5] is the pk flag
                url_is_primary = True
                break
        
        if not url_is_primary:
            logger.info("Recreating visits table with URL as primary key")
            # Backup existing data
            cursor.execute("SELECT url, title, timestamp, content_hash, text_extract, links FROM visits")
            old_visits = cursor.fetchall()
            
            # Drop the old table
            cursor.execute("DROP TABLE visits")
            
            # Create new table with URL as primary key
            cursor.execute('''
            CREATE TABLE visits (
                url TEXT PRIMARY KEY,
                title TEXT,
                timestamp TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                text_extract TEXT,
                links TEXT,
                processed BOOLEAN DEFAULT 1
            )
            ''')
            
            # Restore data (only the most recent visit for each URL)
            url_seen = set()
            for visit in reversed(old_visits):  # Process in reverse to keep most recent
                if visit['url'] not in url_seen:
                    cursor.execute(
                        "INSERT INTO visits (url, title, timestamp, content_hash, text_extract, links, processed) VALUES (?, ?, ?, ?, ?, ?, 1)",
                        (visit['url'], visit['title'], visit['timestamp'], visit['content_hash'], 
                         visit['text_extract'], visit.get('links'))
                    )
                    url_seen.add(visit['url'])
    else:
        # Create new table with URL as primary key
        cursor.execute('''
        CREATE TABLE visits (
            url TEXT PRIMARY KEY,
            title TEXT,
            timestamp TEXT NOT NULL,
            content_hash TEXT NOT NULL,
            text_extract TEXT,
            links TEXT,
            processed BOOLEAN DEFAULT 1
        )
        ''')
    
    conn.commit()
    conn.close()
    logger.info("Database initialized successfully")

def backup_db():
    """Backup the database to a file periodically"""
    while True:
        time.sleep(300)  # Every 5 minutes
        try:
            # Connect to in-memory DB
            src = get_db_connection()
            # Connect to file DB
            dest = sqlite3.connect(Config.PERSIST_DB_PATH)
            # Copy data
            src.backup(dest)
            dest.close()
            src.close()
            logger.info(f"Database backed up to {Config.PERSIST_DB_PATH}")
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")

# Start backup thread if persistence is desired
if Config.PERSIST_DB:
    backup_thread = threading.Thread(target=backup_db, daemon=True)
    backup_thread.start()
    logger.info("Database persistence enabled") 