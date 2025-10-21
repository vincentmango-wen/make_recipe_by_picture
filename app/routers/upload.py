# app/routers/upload.py
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from pathlib import Path
from app.utils import parse_ingredients_from_response

router = APIRouter(prefix="/upload", tags=["upload"])

# サーバレスではローカル保存を行わない


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    """
    画像をアップロードして保存し、擬似的に食材リストを返すAPI。
    本来は画像解析モデルやOpenAI APIを呼び出す部分。
    """

    # 拡張子チェック
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only .jpg/.png files are allowed")

    # サーバレスではファイルは保存せず、必要なら bytes をそのまま扱う
    try:
        _ = await file.read()
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to read image")

    # TODO: 本来はAIで食材検出する処理
    dummy_ingredients = ["tomato", "onion", "chicken"]

    return JSONResponse({
        "filename": file.filename,
        "saved_path": None,
        "ingredients": dummy_ingredients,
    })
