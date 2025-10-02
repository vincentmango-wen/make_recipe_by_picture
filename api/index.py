# api/index.py
# Vercel の Python runtime は 'app' 変数を探します。
# 既に app/main.py に FastAPI の app があるならそれを import して再公開します。

from app.main import app  # repo の構成に合わせてパスを調整

# もし app.main に app がない場合は下記の最小例を一時的に置いて動作確認してください
from fastapi import FastAPI
app = FastAPI()
@app.get("/")
def root():
    return {"message": "Hello from FastAPI on Vercel"}
