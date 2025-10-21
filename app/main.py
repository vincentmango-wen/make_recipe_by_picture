# app/main.py
from fastapi import FastAPI, Request, Form, UploadFile, File
from pathlib import Path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
import os
import base64
from dotenv import load_dotenv
from app.utils import get_openai_client, parse_ingredients_from_response, save_b64_image

from app.routers import upload, generate, image_gen

# FastAPIアプリ本体を生成
# ※タイトルや説明は自動生成のドキュメント(/docs)に反映されます
app = FastAPI(
    title="食材画像からレシピ提案アプリ",
    description="画像から食材を検出し、レシピを提案・保存するAPI（MVP）",
    version="0.1.0",
)
# データベース初期化は不要（MVP仕様）

# MVP機能のルーターを追加
app.include_router(upload.router)
app.include_router(generate.router)
app.include_router(image_gen.router)

# /static というURLパスで、プロジェクト内の static/ フォルダを公開する
# 生成した料理画像などをブラウザから見られるようにしておく

# CSSやJSなどの静的ファイルを /static にマウント（app/static フォルダを公開）
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# DB初期化は startup イベントでのみ実行


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    トップ画面（画像アップロードフォーム）
    """
    return templates.TemplateResponse("index.html", {"request": request})

# --------------------------------------------------------------
# 画像アップロード（UI向け）
# --------------------------------------------------------------
@app.post("/upload_ui", response_class=HTMLResponse)
async def upload_ui(request: Request, file: UploadFile = File(...)):

    # --- Vision API呼び出し ---
    load_dotenv()
    client = get_openai_client()

    prompt = """
    この画像に写っている食材をリストアップしてください。
    食材名だけを日本語で返してください。
    例: ["トマト","玉ねぎ","鶏肉"]
    """

    img_bytes = await file.read()

    response = client.chat.completions.create(
        model="gpt-4o-mini",   # Vision対応モデル
        messages=[
            {"role": "system", "content": "あなたは料理の食材を見分けるアシスタントです。"},
            {"role": "user", "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")}}
            ]}
        ],
        max_tokens=200
    )

    # 返答から食材リストを抽出
    content = response.choices[0].message.content.strip()
    ingredients = parse_ingredients_from_response(content)

    # UI にはデータURLで表示（サーバレスでローカル静的配信に依存しない）
    image_data_url = "data:image/jpeg;base64," + base64.b64encode(img_bytes).decode("utf-8")

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "image_url": image_data_url,
            "ingredients": ingredients,
        },
    )

# ----------------------------
# レシピ生成（UI向け）
# ----------------------------
@app.post("/generate_ui", response_class=HTMLResponse)
async def generate_ui(
    request: Request, 
    ingredients: str = Form(...)
    ):
    load_dotenv()
    client = get_openai_client()

    ingredient_list = [i.strip() for i in ingredients.split(",") if i.strip()]

    # ---------- レシピ生成 ----------
    prompt = f"""
    以下の食材を使って、日本語で家庭料理のレシピを提案してください。
    出力形式は次のようにしてください:
    料理名: ○○
    材料: ○○
    手順: ○○
    ---
    食材: {", ".join(ingredient_list)}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたは優秀な料理アシスタントです。"},
            {"role": "user", "content": prompt},
        ],
    )
    recipe_text = response.choices[0].message.content

    # ---------- 料理名を抽出 ----------
    import re
    title_match = re.search(r"料理名[:：]\s*(.+)", recipe_text)
    title = title_match.group(1).strip() if title_match else "料理"

    # ---------- 料理画像生成 ----------
    image_response = client.images.generate(
        model="dall-e-3",
        prompt=f"{title} の料理の完成品イメージ写真、日本家庭料理風",
        size="1024x1024",
        response_format="b64_json",
    )

    img_b64 = image_response.data[0].b64_json
    image_url = save_b64_image(img_b64, title=title)

    return templates.TemplateResponse(
        "recipe.html",
        {
            "request": request,
            "ingredients": ingredient_list,
            "recipe": recipe_text,
            "image_url": image_url,
        },
    )

# MVP仕様：データベース関連機能は削除