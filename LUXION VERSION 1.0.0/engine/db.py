"""
Database module for Luxion
Optimized for PyInstaller
"""

import sqlite3
import os

def get_db_path():
    """Get database path that works for both dev and PyInstaller"""
    # Try different locations
    paths_to_try = [
        "sophia.db",  # Current directory
        os.path.join(os.path.dirname(__file__), "..", "sophia.db"),  # Parent directory
        os.path.join(os.getcwd(), "sophia.db"),  # Working directory
    ]
    
    for path in paths_to_try:
        if os.path.exists(path):
            return path
    
    # If not found, create in current directory
    return "sophia.db"

def init_database():
    """Initialize database with default data"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS sys_command
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name VARCHAR(100) UNIQUE,
                      path VARCHAR(1000),
                      process_name VARCHAR(100))''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS web_command
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      name VARCHAR(100) UNIQUE,
                      url VARCHAR(1000))''')
    
    # Insert default apps if table is empty
    cursor.execute('SELECT COUNT(*) FROM sys_command')
    if cursor.fetchone()[0] == 0:
        default_apps = [
            ('chrome', 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe', 'chrome.exe'),
            ('firefox', 'C:\\Program Files\\Mozilla Firefox\\firefox.exe', 'firefox.exe'),
            ('notepad', 'notepad.exe', 'notepad.exe'),
            ('calculator', 'calc.exe', 'calculator.exe'),
            ('cmd', 'cmd.exe', 'cmd.exe'),
            ('paint', 'mspaint.exe', 'mspaint.exe'),
        ]
        
        cursor.executemany('INSERT OR IGNORE INTO sys_command (name, path, process_name) VALUES (?, ?, ?)', 
                          default_apps)
    
    # Insert default websites
    cursor.execute('SELECT COUNT(*) FROM web_command')
    if cursor.fetchone()[0] == 0:
        default_websites = [
            ('youtube', 'https://youtube.com'),
            ('google', 'https://google.com'),
            ('facebook', 'https://facebook.com'),
            ('github', 'https://github.com'),
            ('gmail', 'https://gmail.com'),
        ]
        
        cursor.executemany('INSERT OR IGNORE INTO web_command (name, url) VALUES (?, ?)', 
                          default_websites)
    
    conn.commit()
    conn.close()
    print(f"✅ Database initialized at {db_path}")

def get_connection():
    """Get database connection"""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Enable dictionary-like access
    return conn

# Convenience functions
def get_app_path(app_name):
    """Get application path by name"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT path FROM sys_command WHERE LOWER(name) = ?', (app_name.lower(),))
    result = cursor.fetchone()
    conn.close()
    return result['path'] if result else None

def get_website_url(site_name):
    """Get website URL by name"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT url FROM web_command WHERE LOWER(name) = ?', (site_name.lower(),))
    result = cursor.fetchone()
    conn.close()
    return result['url'] if result else None

def add_app(name, path, process_name=None):
    """Add new application to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO sys_command (name, path, process_name) VALUES (?, ?, ?)',
                  (name.lower(), path, process_name or f"{name.lower()}.exe"))
    conn.commit()
    conn.close()

def add_website(name, url):
    """Add new website to database"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO web_command (name, url) VALUES (?, ?)',
                  (name.lower(), url))
    conn.commit()
    conn.close()

# Test module
if __name__ == "__main__":
    init_database()
    print("Database ready!")