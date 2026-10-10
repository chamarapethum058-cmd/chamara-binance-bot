import os
from dotenv import load_dotenv

load_dotenv()

# Determine absolute path to falcon.db
_curr_dir = os.path.dirname(os.path.abspath(__file__))
_parent_dir = os.path.dirname(_curr_dir)
_db_file = os.path.join(_parent_dir, "falcon.db")
if not os.path.exists(_db_file):
    _db_file = os.path.join(os.getcwd(), "falcon.db")

_default_sqlite = f"sqlite:///{_db_file.replace(os.sep, '/')}"

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", _default_sqlite)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    BINANCE_API_URL: str = "https://api.binance.com"
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")

settings = Settings()
