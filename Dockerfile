# ベースイメージ
FROM python:3.11-slim

WORKDIR /app

# 必要パッケージのインストール（apt が必要ならここで）
RUN apt-get update && apt-get install -y build-essential gcc --no-install-recommends && rm -rf /var/lib/apt/lists/*

# 依存関係をコピーしてインストール
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# アプリをコピー
COPY . /app

# 環境変数 PORT がなければ 8000 を使用
ENV PORT=${PORT:-8000}

# uvicorn を起動（環境変数 PORT を使う）
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --proxy-headers"]