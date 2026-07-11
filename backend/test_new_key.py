import sqlite3
from google import genai

conn = sqlite3.connect("falcon.db")
cursor = conn.cursor()
cursor.execute("SELECT value FROM preferences WHERE key='gemini_api_key'")
row = cursor.fetchone()
conn.close()

if not row:
    print("No key found in database.")
    exit(1)

key = row[0]
print("Testing Key:", key)

try:
    client = genai.Client(api_key=key)
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents="Hello"
    )
    print("SUCCESS! Response:", response.text)
except Exception as e:
    print("FAILED:", str(e))
