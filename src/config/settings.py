#src/config/settings.py
import os
from dotenv import load_dotenv

# load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    # DB_FILE = os.getenv("DB_FILE", "expenses.db")

    API_URL = os.getenv("API_URL", "http://localhost:8000/chat")

    DATABASE_URL = os.getenv("DATABASE_URL","")

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")


    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")

settings = Settings()
