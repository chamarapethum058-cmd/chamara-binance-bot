import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "falcon.db")
print("Migrating DB at:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("ALTER TABLE logged_trades ADD COLUMN strategy_type VARCHAR DEFAULT 'SMC'")
    conn.commit()
    print("Successfully added strategy_type column!")
except Exception as e:
    print("Migration status/error:", e)
finally:
    conn.close()
