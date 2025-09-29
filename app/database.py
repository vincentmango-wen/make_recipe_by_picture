# app/database.py
from sqlmodel import SQLModel, create_engine, Session
import os

# 環境変数 DATABASE_URL を優先して使用。なければローカルの SQLite を使う
DATABASE_URL = os.getenv("DATABASE_URL") or "sqlite:///./recipes.db"

# connect_args は SQLite のみ指定
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# エンジン作成（echo=TrueでSQLログが見える：開発時は便利）
engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)


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
