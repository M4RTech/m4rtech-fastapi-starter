from sqlalchemy import text
from app.db.session import engine

def init_db() -> None:
    # proste "ping" do DB – sprawdza czy engine działa
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
