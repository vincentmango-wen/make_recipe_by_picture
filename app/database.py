# app/database.py
from sqlmodel import SQLModel, create_engine, Session

# SQLite のDBファイルを指定（ローカル保存）
DATABASE_URL = "sqlite:///./recipes.db"

# エンジン作成（echo=TrueでSQLログが見える：開発時は便利）
engine = create_engine(DATABASE_URL, echo=True)


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
