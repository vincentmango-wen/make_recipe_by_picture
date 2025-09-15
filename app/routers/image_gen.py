# app/routers/image_gen.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import base64
from openai import OpenAI
from dotenv import load_dotenv

# .env読み込み
load_dotenv()

router = APIRouter(prefix="/image", tags=["image"])

# OpenAIクライアント
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set")
client = OpenAI(api_key=api_key)

# 保存先
OUTPUT_DIR = Path("static/generated")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class ImageRequest(BaseModel):
    title: str
    ingredients: list[str]


@router.post("/")
def generate_image(req: ImageRequest):
    """
    レシピ名と食材リストを受け取り、DALL·Eで完成品イメージ画像を生成するAPI
    """
    if not req.title:
        raise HTTPException(status_code=400, detail="Title is required")

    prompt = f"料理名: {req.title}\n食材: {', '.join(req.ingredients)}\n\n日本の家庭料理風の完成品写真を生成してください。"

    try:
        response = client.images.generate(
            model="dall-e-3",  # DALL·E 3相当
            prompt=prompt,
            size="1024x1024",
            response_format="b64_json",
        )

        # Base64から画像に変換
        img_b64 = response.data[0].b64_json
        img_bytes = base64.b64decode(img_b64)

        # 保存パス
        filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{req.title}.png"
        save_path = OUTPUT_DIR / filename

        with open(save_path, "wb") as f:
            f.write(img_bytes)

        return JSONResponse({
            "status": "success",
            "title": req.title,
            "ingredients": req.ingredients,
            "image_url": f"/static/generated/{filename}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
