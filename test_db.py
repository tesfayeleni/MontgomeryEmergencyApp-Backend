import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent / ".env", override=True)

print("USER:", os.getenv("POSTGRES_USER"))
print("HOST:", os.getenv("POSTGRES_HOST"))
print("PORT:", os.getenv("POSTGRES_PORT"))
print("DB:  ", os.getenv("POSTGRES_DB"))
print("PASS:", os.getenv("POSTGRES_PASSWORD"))

from sqlalchemy import text
from app.db.database import engine

with engine.connect() as conn:
    result = conn.execute(text("SELECT 1"))
    print("Connected!", result.fetchone())
