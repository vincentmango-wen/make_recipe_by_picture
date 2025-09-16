# app/routers/image_gen.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import base64
from app.utils import get_openai_client, save_b64_image

router = APIRouter(prefix="/image", tags=["image"])


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

    client = get_openai_client()
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            response_format="b64_json",
        )

        img_b64 = response.data[0].b64_json
        save_path = save_b64_image(img_b64, title=req.title)

        return JSONResponse({
            "status": "success",
            "title": req.title,
            "ingredients": req.ingredients,
            "image_url": f"/static/generated/{save_path.name}"
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
