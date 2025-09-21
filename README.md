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
