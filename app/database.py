# app/database.py
from sqlmodel import SQLModel, create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

# Read raw DATABASE_URL from environment (may be None)
raw_database_url = os.getenv("DATABASE_URL")

# If provided, normalize common Postgres scheme variants. Some providers
# (Heroku, older libs) return "postgres://..." which SQLAlchemy treats as
# legacy; prefer explicit driver scheme for psycopg2.
if raw_database_url:
    DATABASE_URL = raw_database_url
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)
else:
    # Fallback to local SQLite for development when DATABASE_URL is not set
    DATABASE_URL = "sqlite:///./recipes.db"

# connect_args are required only for SQLite
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# Enable pool_pre_ping to avoid "connection is closed" / stale connection
# issues with long-lived Postgres connections (useful for production).
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args, pool_pre_ping=True)


def init_db():
    """
    モデルで定義したテーブルをSQLiteに作成する関数。
    初回起動時に呼び出す。
    """
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    DB操作用のセッションを返す関数。
    API内でDBアクセスするときに使う。
    """
    with Session(engine) as session:
        yield session
