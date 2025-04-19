# test_db_connection.py
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL"))

try:
    with engine.connect() as conn:
        print("✅ Connected to PostgreSQL on Render!")
except Exception as e:
    print("❌ Connection failed:", e)
