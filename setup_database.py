import sqlite3
from datetime import datetime

def setup_database():
    # Connect to SQLite database (or create it)
    conn = sqlite3.connect('face_recognition.db')
    cursor = conn.cursor()

    # Drop existing table if it exists
    cursor.execute('DROP TABLE IF EXISTS users')

    # Create users table with new schema
    cursor.execute('''
    CREATE TABLE users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT,
        phone TEXT,
        registered_date DATETIME DEFAULT CURRENT_TIMESTAMP,
        image_path TEXT,
        face_encoding BLOB NOT NULL
    )
    ''')

    conn.commit()
    print("Database schema updated successfully!")

    # Create indexes for frequently accessed columns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON users(name)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_email ON users(email)')
    
    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_database()