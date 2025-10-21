# api/index.py
# Vercel の Python runtime は 'app' 変数を探します。
# 既に app/main.py に FastAPI の app があるならそれを import して再公開します。

from app.main import app  # repo の構成に合わせてパスを調整
