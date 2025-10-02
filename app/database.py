# ...existing code...
from typing import Generator
import os
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine
from sqlalchemy import event
from urllib.parse import urlsplit, urlunsplit, parse_qs

# 環境変数から取得
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()

# 補正: "postgres://" -> "postgresql+pg8000://"（純Pythonドライバ pg8000 を使う）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+pg8000://", 1)

# 初期設定
SQLALCHEMY_DATABASE_URL = ""
connect_args = {}

if DATABASE_URL:
    # parse URL to handle query params (sslmode 等)
    parts = urlsplit(DATABASE_URL)
    qs = parse_qs(parts.query)

    # pg8000 が使われる場合: sslmode を取り出して connect_args に反映し、URL からは削除する
    if parts.scheme.startswith("postgresql+pg8000"):
        if "sslmode" in qs:
            # sslmode=require なら SSL を有効にする
            val = qs.get("sslmode", [""])[0].lower()
            if val in ("require", "verify-ca", "verify-full", "true", "1"):
                connect_args["ssl"] = True
        # URL のクエリを除去して再構築（ドライバに不適合なクエリを渡さないため）
        SQLALCHEMY_DATABASE_URL = urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
    else:
        # その他のスキームはそのまま使う
        SQLALCHEMY_DATABASE_URL = DATABASE_URL
else:
    SQLALCHEMY_DATABASE_URL = "sqlite:///./recipes.db"

# SQLite の場合は check_same_thread が必要
if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    connect_args.update({"check_same_thread": False})

# engine 作成
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