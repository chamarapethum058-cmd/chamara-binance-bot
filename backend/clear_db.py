import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "falcon.db")
print("Clearing logged_trades at:", db_path)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()
try:
    cursor.execute("DELETE FROM logged_trades")
    conn.commit()
    print("Successfully deleted all entries from logged_trades!")
except Exception as e:
    print("Error clearing DB:", e)
finally:
    conn.close()
