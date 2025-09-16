# app/routers/upload.py
import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime
from pathlib import Path
from PIL import Image
from app.utils import save_upload_file

router = APIRouter(prefix="/upload", tags=["upload"])

# 保存先ディレクトリ
UPLOAD_DIR = Path("app/static/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/")
async def upload_image(file: UploadFile = File(...)):
    """
    画像をアップロードして保存し、擬似的に食材リストを返すAPI。
    本来は画像解析モデルやOpenAI APIを呼び出す部分。
    """

    # 拡張子チェック
    if not file.filename.lower().endswith((".jpg", ".jpeg", ".png")):
        raise HTTPException(status_code=400, detail="Only .jpg/.png files are allowed")

    # 保存ファイル名（タイムスタンプ付き）
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    save_path = UPLOAD_DIR / f"{timestamp}_{file.filename}"

    try:
        save_path = save_upload_file(file)
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to process image")

    # TODO: 本来はAIで食材検出する処理
    dummy_ingredients = ["tomato", "onion", "chicken"]

    return JSONResponse({
        "filename": file.filename,
        "saved_path": str(save_path),
        "ingredients": dummy_ingredients,
    })
