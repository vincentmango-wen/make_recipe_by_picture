# API 設計書

## 📘 プロジェクト名

食材画像からレシピ提案アプリ

---

## 1. 使用技術

- **フレームワーク**：FastAPI
- **AI API**：OpenAI API（GPT-4o-mini / DALL·E）
- **DB**：SQLite（レシピ保存用）
- **レスポンス形式**：JSON

---

## 2. エンドポイント一覧

| No  | エンドポイント           | メソッド | 機能概要                                     |
| --- | ------------------------ | -------- | -------------------------------------------- |
| 1   | `/upload`                | POST     | 食材画像をアップロードし、食材検出処理を行う |
| 2   | `/ingredients`           | GET      | 検出された食材リストを取得                   |
| 3   | `/recipes`               | POST     | 食材リストをもとにレシピを生成               |
| 4   | `/recipes`               | GET      | 保存済みレシピ一覧を取得                     |
| 5   | `/recipes/{id}`          | GET      | 指定したレシピの詳細を取得                   |
| 6   | `/recipes/{id}`          | DELETE   | 指定したレシピを削除                         |
| 7   | `/recipes/{id}`          | PUT      | 指定したレシピを更新                         |
| 8   | `/recipes/{id}/favorite` | POST     | 指定したレシピをお気に入り登録/解除          |
| 9   | `/recipes/{id}/image`    | POST     | 指定したレシピの完成品イメージ画像を生成     |

---

## 3. リクエスト/レスポンス仕様

### 3.1 `/upload` (POST)

- **概要**：画像をアップロードし、サーバーで食材検出を実行
- **リクエスト**

  ```http
  POST /upload
  Content-Type: multipart/form-data

  file: (jpg/png画像)

  ```

- **レスポンス**
  ```json
  {
    "ingredients": ["tomato", "onion", "chicken"]
  }
  ```

### 3.2`/ingredients`(GET)

- **概要**:直前にアップロードした画像から検出された食材を取得
- **レスポンス**
  ```json
  {
    "ingredients": ["tomato", "onion", "chicken"]
  }
  ```

### 3.3`/recipes`(POST)

- **概要**:食材リストを入力してレシピを生成
- **リクエスト**
  ```json
  {
    "ingredients": ["tomato", "onion", "chicken"]
  }
  ```
- **レスポンス**
  ```json
  {
    "recipes": [
      {
        "title": "トマトチキンカレー",
        "ingredients": ["tomato", "onion", "chicken", "curry powder"],
        "steps": [
          "玉ねぎを炒める",
          "鶏肉を加える",
          "トマトとスパイスを入れる",
          "煮込む"
        ],
        "image_url": "/static/generated/recipe1.png"
      }
    ]
  }
  ```

### 3.4`/recipes`(GET)

- **概要**:保存済みレシピ一覧を取得
- **レスポンス**:
  ```json
  {
    "recipes": [
      {
        "id": 1,
        "title": "トマトチキンカレー",
        "created_at": "2025-09-15",
        "favorite": true
      },
      {
        "id": 2,
        "title": "オニオンスープ",
        "created_at": "2025-09-14",
        "favorite": false
      }
    ]
  }
  ```

### 3.5`/recipes/{id}`(GET)

- **概要**:保存済みレシピの詳細を取得
- **レスポンス**
  ```json
  {
    "id": 1,
    "title": "トマトチキンカレー",
    "ingredients": ["tomato", "onion", "chicken", "curry powder"],
    "steps": [
      "玉ねぎを炒める",
      "鶏肉を加える",
      "トマトとスパイスを入れる",
      "煮込む"
    ],
    "image_url": "/static/generated/recipe1.png",
    "favorite": true,
    "tags": ["カレー", "簡単"]
  }
  ```

### 3.6`/recipes/{id}`(DELETE)

- **概要**:保存済みレシピを削除
- **レスポンス**
  ```json
  {
    "status": "success",
    "message": "Recipe deleted"
  }
  ```

### 3.7`/recipes/{id}`(PUT)

- **概要**:保存済みレシピを更新（材料や手順を編集可能）
- **リクエスト**
  ```json
  {
    "title": "改良版トマトチキンカレー",
    "ingredients": ["tomato", "onion", "chicken", "garlic"],
    "steps": ["材料を準備する", "炒める", "煮込む"]
  }
  ```

### 3.8`/recipes/{id}/favorite`(POST)

- **概要**:レシピをお気に入り登録/解除
- **リクエスト**
  ```json
  {
    "favorite": true
  }
  ```
- **レスポンス**
  ```json
  {
    "status": "success",
    "message": "Recipe marked as favorite"
  }
  ```

### 3.9`/recipes/{id}/image(POST)

- **概要**:レシピをもとに完成品イメージ画像を生成（DALL-E API 利用）
- **レスポンス**
  ```json
  {
    "status": "success",
    "image_url": "/static/generated/recipe1.png"
  }
  ```
