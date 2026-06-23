import sqlite3
import os

DB_FILE = "softlend.db"
MIGRATION_FILE = "migrations/001_init.sql"

def run_migration():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    with open(MIGRATION_FILE, 'r') as f:
        sql_script = f.read()
        cursor.executescript(sql_script)
    
    conn.commit()
    conn.close()
    print("Migration executed successfully. Database created.")

if __name__ == "__main__":
    run_migration()
