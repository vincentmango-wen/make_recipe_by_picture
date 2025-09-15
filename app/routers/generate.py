# app/routers/generate.py
import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

# .envファイルを読み込む
load_dotenv()
opejnai_api_key = os.getenv("OPENAI_API_KEY")
print(os.getenv("OPENAI_API_KEY"))  # 確認用

router = APIRouter(prefix="/generate", tags=["generate"])

# OpenAIクライアント
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY is not set in environment variables")
client = OpenAI(api_key=api_key)


class GenerateRequest(BaseModel):
    ingredients: List[str]


@router.post("/")
def generate_recipe(req: GenerateRequest):
    """
    食材リストを受け取り、OpenAI APIを使ってレシピを生成するAPI
    """
    if not req.ingredients:
        raise HTTPException(status_code=400, detail="Ingredients list cannot be empty")

    # プロンプト作成
    prompt = f"""
    以下の食材を使って、家庭で簡単に作れる日本語レシピを1つ提案してください。
    必ず以下の形式で出力してください：
    ---
    料理名: <料理名>
    材料: <カンマ区切りリスト>
    手順: <番号付き手順>
    ---

    食材: {", ".join(req.ingredients)}
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "あなたは優秀な料理アシスタントです。"},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
        )

        recipe_text = response.choices[0].message.content

        return JSONResponse({
            "ingredients": req.ingredients,
            "recipe": recipe_text
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
