import json
import os
from datetime import datetime
import sqlite3

# Path to the data directory and blocklist file
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)
BLOCKLIST_FILE = os.path.join(DATA_DIR, 'blocklist.json')

# Assuming you have a connection to your database
conn = sqlite3.connect('visits.db', check_same_thread=False)
cursor = conn.cursor()

def get_blocklist():
    """Get all entries from the blocklist file"""
    if not os.path.exists(BLOCKLIST_FILE):
        return []
    
    with open(BLOCKLIST_FILE, 'r') as f:
        return json.load(f)

def add_to_blocklist(url, reason=None):
    """Add a new entry to the blocklist file if it doesn't already exist"""
    # Read existing blocklist
    if os.path.exists(BLOCKLIST_FILE):
        with open(BLOCKLIST_FILE, 'r') as f:
            blocklist = json.load(f)
    else:
        blocklist = []
    
    # Check if URL already exists in blocklist
    for existing in blocklist:
        if existing["url"] == url:
            # URL already exists, update reason if provided
            if reason:
                existing["reason"] = reason
                # Update timestamp
                existing["added"] = datetime.now().isoformat()
            
            # Write back to file
            with open(BLOCKLIST_FILE, 'w') as f:
                json.dump(blocklist, f, indent=2)
            
            return existing
    
    # URL doesn't exist, create new entry
    entry = {
        "url": url,
        "reason": reason or "Blocked from API",
        "added": datetime.now().isoformat()
    }
    
    # Add to blocklist
    blocklist.append(entry)
    
    # Write back to file
    with open(BLOCKLIST_FILE, 'w') as f:
        json.dump(blocklist, f, indent=2)
    
    return entry

def remove_from_blocklist(index):
    """Remove an entry from the blocklist by index"""
    if not os.path.exists(BLOCKLIST_FILE):
        raise FileNotFoundError("Blocklist file does not exist")
    
    with open(BLOCKLIST_FILE, 'r') as f:
        blocklist = json.load(f)
    
    if index < 0 or index >= len(blocklist):
        raise IndexError("Invalid blocklist entry index")
    
    # Remove the entry
    removed = blocklist.pop(index)
    
    # Write back to file
    with open(BLOCKLIST_FILE, 'w') as f:
        json.dump(blocklist, f, indent=2)
    
    return removed

def clear_blocklist():
    with open(BLOCKLIST_FILE, 'w') as file:
        json.dump([], file) 