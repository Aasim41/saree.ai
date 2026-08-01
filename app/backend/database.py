import sqlite3
import os

DB_FILE = "texflow_assets.db"

def init_db():
    # Remove old prototype DB if it exists
    if os.path.exists("saree_assets.db"):
        try: os.remove("saree_assets.db")
        except: pass
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            collection TEXT,
            fabric_type TEXT,
            print_width_cm INTEGER,
            repeat_size_cm INTEGER,
            palette TEXT,
            parent_id INTEGER,
            image_path TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(parent_id) REFERENCES assets(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_asset(name, collection, fabric_type, print_width_cm, repeat_size_cm, palette, parent_id, image_path):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        INSERT INTO assets (name, collection, fabric_type, print_width_cm, repeat_size_cm, palette, parent_id, image_path)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (name, collection, fabric_type, print_width_cm, repeat_size_cm, palette, parent_id, image_path))
    last_id = c.lastrowid
    conn.commit()
    conn.close()
    return last_id

def get_assets():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM assets ORDER BY created_at DESC')
    rows = c.fetchall()
    conn.close()
    return [dict(ix) for ix in rows]

def get_asset(asset_id):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT * FROM assets WHERE id = ?', (asset_id,))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None
