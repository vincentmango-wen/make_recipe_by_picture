# 食材画像からレシピ提案アプリ 🍳

## 📘 プロジェクト概要

このアプリは、ユーザーがアップロードした **食材の写真** から食材を自動検出し、  
その食材を使った **おすすめレシピ** を生成・保存できるサービスです。

- **フレームワーク**: FastAPI
- **AI モデル**: OpenAI API（GPT-4o-mini, DALL·E）
- **DB**: SQLite
- **対象ユーザー**: 日々の献立に悩む人、冷蔵庫の余り食材を有効活用したい人

---

## ✨ 主な機能

- 画像アップロード → 食材検出
- 食材リストをもとにしたレシピ提案（AI 生成）
- レシピの詳細表示（材料・手順・完成品イメージ）
- レシピの保存・検索・編集・削除
- お気に入り登録（スター付与）

---

## 🚀 セットアップ手順

### 1. リポジトリをクローン

```bash
git clone https://github.com/your-repo/recipe-app.git
cd recipe-app
```

### 2. 仮想環境を作成

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 3. パッケージをインストール

```bash
pip install -r requirements.txt
```

### 4. 環境変数を設定

.env ファイルを作成し、以下を記載してください：

```env
OPENAI_API_KEY=sk-xxxxxxx
```

### 5. アプリを起動

```bash
uvicorn app.main:app --reload
```

アクセス URL: http://127.0.0.1:8000

Swagger UI（API ドキュメント）: http://127.0.0.1:8000/docs

📂 ディレクトリ構成

```bash
recipe-app/
├─ app/
│  ├─ main.py              # エントリーポイント
│  ├─ routers/             # APIルーター
│  ├─ services/            # ビジネスロジック
│  ├─ models/              # DBモデル
│  ├─ database.py          # DB接続設定
│  ├─ schemas.py           # Pydanticスキーマ
│  └─ utils.py             # 共通関数
├─ static/                 # 生成画像保存先
├─ tests/                  # テストコード
├─ requirements.txt        # 依存ライブラリ
├─ .env                    # 環境変数ファイル
└─ README.md
```

🧪 テスト

```bash
pytest tests/
```

🛠 今後の拡張予定

- ユーザー認証機能（ログイン/ログアウト）

- 複数ユーザーでのレシピ共有

- 栄養計算やカロリー表示

- 外部 API との連携（例: クックパッド風データ検索）

📄 ライセンス

MIT License
