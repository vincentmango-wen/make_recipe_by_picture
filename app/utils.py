import os
from pathlib import Path
from datetime import datetime
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI

# Optional S3 support
import boto3
from botocore.exceptions import BotoCoreError, ClientError
import typing


def _ensure_dir(path: str | Path):
    p = Path(path)
    # Avoid attempts to create absolute root-level directories like '/static'
    if p.is_absolute() and not str(p).startswith(str(Path.cwd())):
        # If absolute but outside the project, treat as relative to project base
        p = Path.cwd() / p.relative_to(Path('/') )
    p.mkdir(parents=True, exist_ok=True)
    return p


def timestamped_filename(original: str) -> str:
    ts = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"{ts}_{original}"


def save_upload_file(upload_file, upload_dir: str | Path | None = None) -> Path:
    """Save an uploaded file and return Path (serverless-compatible, no PIL).

    Default location is /tmp/uploads for serverless safety. You can override
    via the UPLOAD_DIR environment variable or by passing upload_dir.
    """
    if upload_file is None:
        raise ValueError("upload_file is required")
    
    if upload_dir is None:
        upload_dir = Path(os.getenv("UPLOAD_DIR", "/tmp/uploads"))
    upload_dir = Path(upload_dir)

    _ensure_dir(upload_dir)
    filename = timestamped_filename(getattr(upload_file, "filename", "upload.bin"))
    save_path = upload_dir / filename

    # Write raw bytes without PIL (serverless-friendly)
    try:
        data = upload_file.file.read()
    except Exception:
        # Fallback: some runtimes may require async read upstream
        data = b""
    with open(save_path, "wb") as f:
        f.write(data)
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


def save_b64_image(b64_data: str, title: str) -> str:
    """
    Save base64 image either to configured S3 bucket (if S3_BUCKET env set)
    and return a public URL, or return data URL for Postgres-only setup.
    """
    s3_bucket = os.getenv("S3_BUCKET")
    if s3_bucket:
        # upload to S3
        filename = f"{title}_{int(os.times()[4])}.png"
        s3 = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION", None),
        )
        key = f"generated/{filename}"
        try:
            data = base64.b64decode(b64_data)
            s3.put_object(Bucket=s3_bucket, Key=key, Body=data, ContentType="image/png", ACL="public-read")
            # Return public URL; adjust if using custom domain or CloudFront
            return f"https://{s3_bucket}.s3.amazonaws.com/{key}"
        except (BotoCoreError, ClientError) as e:
            # If upload fails, fall back to data URL
            pass

    # Postgres-only setup: return data URL instead of local file
    return "data:image/png;base64," + b64_data
