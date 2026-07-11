import sqlite3

conn = sqlite3.connect(r"c:\Users\Welcome\Desktop\binance bot\backend\falcon.db")
cursor = conn.cursor()
try:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    print("Tables:", cursor.fetchall())
    
    cursor.execute("PRAGMA table_info(preferences);")
    print("Preferences columns:", cursor.fetchall())
    
    cursor.execute("SELECT * FROM preferences;")
    print("Preferences rows:", cursor.fetchall())
except Exception as e:
    print("Error:", e)
finally:
    conn.close()
