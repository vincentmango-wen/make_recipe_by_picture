# ...existing code...
from typing import Generator
import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine
from sqlalchemy import event

# 環境変数から取得（Vercel の場合 "postgres://" 形式になりがち）
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

# 補正: "postgres://" -> "postgresql+psycopg://"（psycopg v3 を使う場合）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)

# デフォルトはローカル SQLite（開発用）
if DATABASE_URL:
    SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URL = f"sqlite:///./recipes.db"

# SQLite の場合は check_same_thread が必要
connect_args = {}
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# pool_pre_ping を付けると DB 切断時の復旧に有利
engine: Engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False, connect_args=connect_args, pool_pre_ping=True)

# SQLite の場合に Foreign Key を有効化（必要なら）
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_con, _connection_record):
        cursor = dbapi_con.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def init_db() -> None:
    """
    初回テーブル作成用。起動時に呼ぶか、以下のコマンドで実行:
    python -c "from app.database import init_db; init_db()"
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
# ...existing code...