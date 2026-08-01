import sqlite3
import os

DB_FILE = "saree_assets.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS designs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt TEXT,
            motif TEXT,
            palette TEXT,
            border TEXT,
            pallu TEXT,
            image_b64 TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_design(prompt, motif, palette, border, pallu, image_b64):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO designs (prompt, motif, palette, border, pallu, image_b64)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (prompt, motif, palette, border, pallu, image_b64))
    conn.commit()
    conn.close()

def get_history():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM designs ORDER BY created_at DESC LIMIT 50')
    rows = c.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]
