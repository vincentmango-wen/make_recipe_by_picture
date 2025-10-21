# ...existing code...
from typing import Generator
import os
import ssl
import certifi
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.engine import Engine
from sqlalchemy import event
from urllib.parse import urlsplit, urlunsplit, parse_qs

# 環境変数から取得（Supabase対応）
DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Supabase の場合は POSTGRES_URL も確認
if not DATABASE_URL:
    DATABASE_URL = os.environ.get("POSTGRES_URL", "").strip()

# 補正: "postgres://" -> "postgresql+psycopg2://"（純Pythonドライバ psycopg2 を使う）
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg2://", 1)

# 初期設定
SQLALCHEMY_DATABASE_URL = ""
connect_args = {}

if DATABASE_URL:
    # parse URL to handle query params (sslmode 等)
    parts = urlsplit(DATABASE_URL)
    qs = parse_qs(parts.query)

    # psycopg2 が使われる場合: sslmode を取り出して connect_args に反映し、URL からは削除する
    if parts.scheme.startswith("postgresql+psycopg2"):
        if "sslmode" in qs:
            val = qs.get("sslmode", [""])[0].lower()
            if val in ("require", "verify-ca", "verify-full", "true", "1"):
                # 1) まず certifi の CA バンドルで SSLContext を作る（安全）
                try:
                    ctx = ssl.create_default_context(cafile=certifi.where())
                except Exception:
                    ctx = None

                # 2) もし接続時に自己署名チェーンで失敗する場合のために、
                #    環境変数 DB_CA_CERT (base64 PEM) があればファイル化して読み込む（より安全）
                db_ca_b64 = os.environ.get("DB_CA_CERT")
                if db_ca_b64:
                    try:
                        import base64, tempfile
                        ca_pem = base64.b64decode(db_ca_b64)
                        tf = tempfile.NamedTemporaryFile(delete=False)
                        tf.write(ca_pem)
                        tf.flush()
                        tf.close()
                        ctx = ssl.create_default_context(cafile=tf.name)
                    except Exception:
                        pass

                # 3) 最後の手段（開発・一時）で検証無効のコンテキストへフォールバック
                if ctx is None:
                    # NOTE: このフォールバックは安全でない。暫定対応のみ。
                    ctx = ssl._create_unverified_context()

                connect_args["ssl_context"] = ctx
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
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    try:
        print(f"Attempting database connection...")
        print(f"DATABASE_URL: {DATABASE_URL[:20]}..." if DATABASE_URL else "DATABASE_URL not set")
        with Session(engine) as session:
            yield session
    except Exception as e:
        print(f"Database connection error: {e}")
        print(f"DATABASE_URL: {DATABASE_URL[:20]}..." if DATABASE_URL else "DATABASE_URL not set")
        print(f"POSTGRES_URL: {os.getenv('POSTGRES_URL', 'NOT SET')[:20]}...")
        raise
# ...existing code...