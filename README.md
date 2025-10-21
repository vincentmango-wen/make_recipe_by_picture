# 食材画像からレシピ提案アプリ 🍳 (MVP版)

## 📘 プロジェクト概要

このアプリは、ユーザーがアップロードした食材の写真から食材を検出し、検出した食材をもとに AI でレシピを生成する Web アプリです（MVP仕様）。

- フレームワーク: FastAPI
- AI: OpenAI API（GPT-4o-mini + DALL-E 3）
- データベース: なし（MVP仕様）

主な対象は日々の献立に悩む方や、冷蔵庫の余り食材を活用したい方です。

---

## 主な機能（MVP）

- 画像アップロードと食材検出
- 検出食材をもとにしたレシピ提案（AI 生成）
- レシピの表示
- 完成品イメージ画像生成

---

## ディレクトリ構成（MVP版）

MVP仕様の重要箇所を抜粋しています。

```
./
├─ app/
│  ├─ main.py           # FastAPI アプリのエントリーポイント
│  ├─ utils.py          # 共通ユーティリティ
│  ├─ routers/          # API ルーター（generate, image_gen, upload）
│  ├─ templates/        # Jinja2 テンプレート（HTML）
│  └─ static/           # 静的ファイル
│     ├─ generated/     # AI が生成した完成イメージなど
│     ├─ uploads/       # ユーザーがアップロードした元画像
│     ├─ css/           # スタイルシート
│     └─ images/        # 画像リソース
├─ design_info/         # 設計ドキュメント
├─ requirements.txt     # 必要最小限の依存関係
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

OpenAI API キーを環境変数で指定します。例（`.env` を用いるかシェルで export）：

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

## 使用方法

1. **画像アップロード**: トップページから食材の写真をアップロード
2. **食材検出**: AI が画像から食材を自動検出
3. **レシピ生成**: 検出された食材をもとにレシピを生成
4. **結果表示**: レシピと完成品イメージを表示

---

## 注意／補足

- MVP仕様のため、データベースは使用していません。レシピの保存機能はありません。
- テンプレートは Jinja2 を用いており、`app/templates/` に HTML テンプレートが格納されています。
- 生成された画像は `app/static/generated/` に保存されます。

---

## 今後の拡張候補

- レシピ保存機能の追加（データベース導入）
- 本格的なユーザー認証（ログイン/ログアウト）
- ユーザーごとのレシピ管理・共有
- 栄養計算やカロリー表示の追加
- レシピの評価・コメント機能

---

## ライセンス

MIT License

---

## デプロイ（Render 向け）

MVP仕様のため、シンプルなデプロイが可能です。

### 必要準備

- GitHub リポジトリにコードを push しておく
- Render アカウント（GitHub 連携）

### デプロイ手順

1. GitHub リポジトリを Render に接続
2. Render ダッシュボードで「New » Web Service」を選択
3. リポジトリとブランチを選ぶ
4. Build Command: `pip install -r requirements.txt`
5. Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 環境変数

- `OPENAI_API_KEY` — OpenAI API キー（必須）

### スモークテスト

デプロイが成功したら、公開 URL にアクセスしてトップページが返るかを確認します。

- 例: `https://<your-service>.onrender.com/` にアクセスする
- `/docs` で OpenAPI ドキュメントも確認可能

画像生成・アップロードの基本動作を試すフロー:

1. トップページから画像をアップロード
2. レシピ生成を試す（OpenAI キーが有効であること）
3. 生成された画像が表示されることを確認
