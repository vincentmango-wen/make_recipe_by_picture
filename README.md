# 食材画像からレシピ提案アプリ 🍳

## 📘 プロジェクト概要

このアプリは、ユーザーがアップロードした食材の写真から食材を検出し、検出した食材をもとに AI でレシピを生成・保存する Web アプリです。

- フレームワーク: FastAPI
- AI: OpenAI API（プロジェクトでは GPT 系や画像生成を想定）
- DB: SQLite（ルートに `recipes.db` が存在します）

主な対象は日々の献立に悩む方や、冷蔵庫の余り食材を活用したい方です。

---

## 主な機能

- 画像アップロードと食材検出
- 検出食材をもとにしたレシピ提案（AI 生成）
- レシピの表示・保存・編集・削除
- 生成画像（完成イメージ）の保存と一覧表示

---

## ディレクトリ構成（抜粋）

プロジェクトの重要箇所を抜粋しています。

```
./
├─ app/
│  ├─ main.py           # FastAPI アプリのエントリーポイント
│  ├─ database.py       # SQLite 接続・初期化
│  ├─ models.py         # DB モデル定義
│  ├─ schemas.py        # Pydantic スキーマ
│  ├─ utils.py          # 共通ユーティリティ
│  ├─ routers/          # API ルーター（generate, image_gen, recipes, upload など）
│  └─ templates/        # Jinja2 テンプレート（HTML）
├─ static/
│  ├─ generated/        # AI が生成した完成イメージなど
│  └─ uploads/          # ユーザーがアップロードした元画像
├─ picture/uploads/     # （同様に画像アップロード用ディレクトリ）
├─ recipes.db           # SQLite データベースファイル
├─ requirements.txt
└─ README.md
```

テンプレートは `app/templates/` にあり、生成済み画像は `app/static/generated/` に保存されます。

---

## セットアップと起動

1. 仮想環境を作成してアクティベート

```bash
python -m venv venv
source venv/bin/activate   # macOS / Linux (zsh を含む)
```

2. 依存関係のインストール

```bash
pip install -r requirements.txt
```

3. 環境変数を設定

OpenAI 等の API キーを環境変数で指定します。例（`.env` を用いるかシェルで export）：

```
OPENAI_API_KEY=sk-xxxxxxx
```

4. サーバ起動

```bash
uvicorn app.main:app --reload
```

ブラウザでアクセス: http://127.0.0.1:8000

Swagger UI: http://127.0.0.1:8000/docs

---

## 注意／補足

- データベースはプロジェクトルートの `recipes.db` を使用しています。初回起動時にマイグレーションや初期化処理が必要な場合は `app/database.py` を参照してください。
- 認証関連のバックアップコード (`app/removed_auth_backup/`) が含まれていますが、現在のメインルートでは未使用の可能性があります。
- テンプレートは Jinja2 を用いており、`app/templates/` に HTML テンプレートが格納されています。

---

## 今後の拡張候補

- 本格的なユーザー認証（ログイン/ログアウト）
- ユーザーごとのレシピ管理・共有
- 栄養計算やカロリー表示の追加

---

## ライセンス

MIT License

---

## Deploy to Render (ステップバイステップ)

以下はこの FastAPI アプリを Render にデプロイするための手順（GUI と CLI 両方）です。S3 と Postgres を使った本番想定の構成を示します。

### 必要準備

- GitHub リポジトリにコードを push しておく
- Render アカウント（GitHub 連携）
- AWS アカウント（S3 を使う場合）

### 1) Docker イメージ利用（推奨）

1. GitHub リポジトリを Render に接続
2. Render ダッシュボードで「New » Web Service」を選択
3. リポジトリとブランチを選ぶ
4. Environment: Docker を選択（このリポジトリの `Dockerfile` を使用）
5. Build Command / Start Command は Dockerfile 内で扱われるため特に不要

Render はデフォルトで環境変数 `PORT` を渡します。Dockerfile はこれを利用します。

### 2) Postgres（Render Add-on）を作成

1. Render Dashboard → New → PostgreSQL
2. プランを選択して DB を作成
3. DB が作成されたら、Connection URL（例: postgres://user:pass@host:5432/dbname）をコピー
4. Web Service の Environment で `DATABASE_URL` にこの値を設定

### 3) S3（生成画像保存）を使う（任意だが推奨）

1. AWS コンソールで S3 バケットを作成（公開 or CloudFront を利用する設定を検討）
2. IAM ユーザーを作成し、S3 バケットに put_object/get_object 権限を付与
3. Render の Web Service の Environment に以下を設定
   - `S3_BUCKET` – バケット名
   - `AWS_ACCESS_KEY_ID` – IAM ユーザーのアクセスキー
   - `AWS_SECRET_ACCESS_KEY` – シークレット
   - `AWS_REGION` – バケットのリージョン（例: ap-northeast-1）

このプロジェクトの `app/utils.py` は `S3_BUCKET` が設定されていれば S3 にアップロードし、公開 URL（https://{bucket}.s3.amazonaws.com/…）を返します。必要なら CloudFront やカスタムドメインに合わせてこのロジックを変更してください。

### 4) Render に必要な環境変数（一覧）

- `OPENAI_API_KEY` — OpenAI API キー（必須）
- `DATABASE_URL` — Postgres の接続文字列（本番）
- `S3_BUCKET` — （任意）S3 バケット名
- `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_REGION` — S3 用

ローカル開発では `.env` を利用できますが、本番では Render の Environment セクションに入れてください。

### 5) 初回デプロイ後の DB 初期化（1 回だけ）

Render の Dashboard → Service → Shell から次を実行してテーブルを作成できます:

```bash
python -c "from app.database import init_db; init_db()"
```

※プロダクションでは Alembic を導入してマイグレーション管理することを推奨します。

### 6) スモークテスト

デプロイが成功したら、公開 URL にアクセスしてトップページが返るかを確認します。

- 例: `https://<your-service>.onrender.com/` にアクセスする
- `/docs` で OpenAPI ドキュメントも確認可能

画像生成・アップロードの基本動作を試すフロー:

1. トップページから画像をアップロード（または API 経由で `/image` を呼ぶ）
2. レシピ生成を試す（OpenAI キーが有効であること）
3. 生成された画像が S3 に保存され、Web タンプレートに表示されることを確認

### 7) トラブルシューティング（よくある問題）

- psycopg2 のインストールエラー: Dockerfile に依存パッケージ（libpq-dev, gcc）を追加済みです。ローカルで pip install する場合は事前にこれらを apt-get で入れてください。
- boto3 import error: `boto3` を `requirements.txt` に追加済み。Docker build で自動的に入ります。
- OpenAI の利用制限や API 応答の形式変更: 新しい OpenAI SDK でエンドポイント/パラメータが変わる可能性があるため、API レスポンスの検証を行ってください。

---

もし望むなら、私の方で次を自動で追加できます:

- `render.yaml`（Render の Infrastructure-as-Code）を作成して自動デプロイ設定を保存
- Alembic を導入してマイグレーション管理を追加
- CloudFront + S3 での公開 URL を利用するよう `app/utils.py` をカスタマイズ

どれを優先しますか？
