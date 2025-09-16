import os
from pathlib import Path
from datetime import datetime
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image


def _ensure_dir(path: str | Path):
    p = Path(path)
    p.mkdir(parents=True, exist_ok=True)
    return p


def timestamped_filename(original: str) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{ts}_{original}"


def save_upload_file(upload_file, upload_dir: str = "/static/uploads") -> Path:
    """Save an uploaded file (Pillow used to normalize image) and return Path."""
    _ensure_dir(upload_dir)
    filename = timestamped_filename(upload_file.filename)
    save_path = Path(upload_dir) / filename

    # Use PIL to open and re-save (handles streams and formats)
    img = Image.open(upload_file.file)
    img.save(save_path)
    return save_path


def get_openai_client() -> OpenAI:
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not set in environment variables")
    return OpenAI(api_key=api_key)


def parse_ingredients_from_response(content: str) -> list[str]:
    """Try to parse JSON first, otherwise split by common delimiters."""
    try:
        data = json.loads(content)
        if isinstance(data, list):
            return [str(x) for x in data]
        if isinstance(data, dict) and "ingredients" in data:
            return [str(x) for x in data["ingredients"]]
    except Exception:
        pass
    # fallback
    items = [x.strip("\u30fb- \n") for x in content.replace("\u3001", ",").split(",") if x.strip()]
    return items

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "static" / "generated"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_b64_image(b64_data: str, title: str) -> Path:
    # ファイル名をタイトルベースで生成
    filename = f"{title}_{int(os.times()[4])}.png"
    file_path = UPLOAD_DIR / filename
    
    with open(file_path, "wb") as f:
        f.write(base64.b64decode(b64_data))

    return file_path
