import os
import sys

sys.path.append(r"c:\Users\Welcome\Desktop\binance bot\backend")
os.chdir(r"c:\Users\Welcome\Desktop\binance bot\backend")

from app.database import SessionLocal
from app.models import PreferenceModel

db = SessionLocal()
try:
    pref = db.query(PreferenceModel).filter(PreferenceModel.key == "gemini_api_key").first()
    print("SQLAlchemy Query result:", pref)
    if pref:
        print("Key:", pref.key)
        print("Value:", pref.value)
finally:
    db.close()
