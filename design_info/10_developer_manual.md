# 開発マニュアル（開発者向け）

## 📘 プロジェクト名

食材画像からレシピ提案アプリ

---

## 1. 開発環境の準備

### 1.1 前提条件

- Python 3.10 以上
- pip インストール済み
- OpenAI API キー取得済み
- Git / GitHub 利用可能

### 1.2 リポジトリのクローン

```bash
git clone https://github.com/your-repo/recipe-app.git
cd recipe-app
```

### 1.3 仮想環境の作成と有効化

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

### 1.4 必要パッケージのインストール

```bash
pip install -r requirements.txt
```

---

## 2. 環境変数の設定

.env ファイルを作成し、以下を記載してください：

```env
OPENAI_API_KEY=sk-xxxxxxx
```

---

## 3. アプリの起動方法

```bash
uvicorn main:app --reload
```

起動後、ブラウザで http://127.0.0.1:8000 にアクセス

API ドキュメントは http://127.0.0.1:8000/docs で確認可能（Swagger UI）

---

## 4. ディレクトリ構成（推奨）

```bash
recipe-app/
├─ app/
│  ├─ main.py              # FastAPI エントリーポイント
│  ├─ routers/             # APIルーター
│  │   ├─ upload.py
│  │   ├─ recipes.py
│  │   └─ images.py
│  ├─ services/            # ビジネスロジック
│  │   ├─ detect.py        # 食材検出処理
│  │   ├─ generate.py      # レシピ生成処理
│  │   └─ image_gen.py     # 画像生成処理
│  ├─ models/              # DBモデル(SQLModel)
│  │   ├─ recipe.py
│  │   ├─ ingredient.py
│  │   └─ tag.py
│  ├─ database.py          # DB接続設定
│  ├─ schemas.py           # Pydanticスキーマ
│  └─ utils.py             # 共通関数
├─ static/                 # 生成画像の保存先
├─ tests/                  # pytest用テストコード
├─ requirements.txt        # 依存パッケージ
├─ .env                    # 環境変数ファイル
└─ README.md
```

---

## 5. データベース操作

### 5.1 初期化

```bash
python app/database.py
```

### 5.2 マイグレーション（必要に応じて）

## SQLModel または Alembic を利用

## 6. テスト方法

- 単体テスト

```bash
pytest tests/
```

- API 結合テスト

```bash
pytest tests/test_api.py
```

---

## 7. デプロイ手順（例: Render / Vercel / Railway）

1. GitHub にリポジトリを Push

2. デプロイ先サービスでリポジトリを連携

3. 環境変数（API キーなど）を設定

4. 自動ビルド・デプロイを実行

5. 公開 URL で動作確認

---

## 8. 開発 Tips

- コードスタイル: PEP8 に準拠

- Linter: flake8 推奨

- フォーマッタ: black 推奨

- 型チェック: mypy を利用するとエラー防止になる
