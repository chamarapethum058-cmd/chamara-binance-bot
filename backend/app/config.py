import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./falcon.db")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    BINANCE_API_URL: str = "https://api.binance.com"

settings = Settings()

