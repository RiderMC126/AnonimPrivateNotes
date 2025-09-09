import sqlite3
from datetime import datetime
import os

def init_db():
    db_file = 'db.db'
    db_exists = os.path.exists(db_file)

    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()

    cursor.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='records' ''')
    table_exists = cursor.fetchone()[0] == 1

    if not db_exists:
        print("База данных создана")
    else:
        print("База данных уже была создана")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY,
            content TEXT NOT NULL,
            delete_date DATETIME NOT NULL,
            counter INTEGER NOT NULL
        )
    ''')

    if not table_exists:
        print("Таблица создана")
    
    conn.commit()
    conn.close()