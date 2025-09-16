# app/main.py
from fastapi import FastAPI, Request, Form, UploadFile, File, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List
import os
import base64
from dotenv import load_dotenv
from app.utils import save_upload_file, get_openai_client, parse_ingredients_from_response, save_b64_image

from app.database import init_db, get_session
from app.routers import recipes, upload, generate, image_gen
from app.models import Tag, Recipe, User
from app.schemas import RecipeCreate
from app.routers import auth
from app.routers.auth import get_current_user
from app.core.security import pwd_context, create_access_token
from jose import JWTError, jwt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# FastAPIアプリ本体を生成
# ※タイトルや説明は自動生成のドキュメント(/docs)に反映されます
app = FastAPI(
    title="食材画像からレシピ提案アプリ",
    description="画像から食材を検出し、レシピを提案・保存するAPI（MVP）",
    version="0.1.0",
)

# レシピルーターを追加
app.include_router(recipes.router)
app.include_router(upload.router)
app.include_router(generate.router)
app.include_router(image_gen.router)
app.include_router(auth.router)

# /static というURLパスで、プロジェクト内の static/ フォルダを公開する
# 生成した料理画像などをブラウザから見られるようにしておく
# 画像（生成画像やアップロード）を /picture にマウント
app.mount("/picture", StaticFiles(directory="picture"), name="picture")

# CSSやJSなどの静的ファイルを /static にマウント（app/static フォルダを公開）
app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# DB初期化を一度だけ実行
init_db()

# サインアップ
@app.post("/signup")
def signup(username: str = Form(...), email: str = Form(...), password: str = Form(...), db: Session = Depends(get_session)):
    hashed_pw = pwd_context.hash(password)
    user = User(username=username, email=email, hashed_password=hashed_pw)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"msg": "User created", "user": user.username}

# ログイン
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token({"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


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
    from pathlib import Path
    from PIL import Image
    from datetime import datetime

    # save uploaded file using utility
    save_path = save_upload_file(file)

    # --- Vision API呼び出し ---
    load_dotenv()
    client = get_openai_client()

    prompt = """
    この画像に写っている食材をリストアップしてください。
    食材名だけを日本語で返してください。
    例: ["トマト","玉ねぎ","鶏肉"]
    """

    with open(save_path, "rb") as f:
        img_bytes = f.read()

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

    return templates.TemplateResponse(
        "result.html",
        {
            "request": request,
            "image_url": f"/picture/uploads/{save_path.name}",
            "ingredients": ingredients,
        },
    )

# ----------------------------
# レシピ生成（UI向け）
# ----------------------------
@app.post("/generate_ui", response_class=HTMLResponse)
async def generate_ui(
    request: Request, 
    ingredients: str = Form(...),
    session: Session = Depends(get_session)
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
    save_path = save_b64_image(img_b64, title=title)
    image_url = f"/picture/generated/{save_path.name}"

    tags = session.exec(select(Tag)).all()

    return templates.TemplateResponse(
        "recipe.html",
        {
            "request": request,
            "ingredients": ingredient_list,
            "recipe": recipe_text,
            "image_url": image_url,
            "tags": tags,
        },
    )

from app.database import get_session

# ----------------------------
# 保存済みレシピ一覧
# ----------------------------
@app.get("/recipes_ui", response_class=HTMLResponse)
def list_recipes_ui(
    request: Request,
    fav_only: bool = False,
    session: Session = Depends(get_session)
):
    query = select(Recipe)
    if fav_only:
        query = query.where(Recipe.favorite == True)

    recipes = session.exec(query).all()
    return templates.TemplateResponse(
        "recipes_list.html",
        {"request": request, "recipes": recipes, "fav_only": fav_only},
    )

# ----------------------------
# レシピ詳細表示
# ----------------------------
@app.get("/recipes_ui/{recipe_id}", response_class=HTMLResponse)
def recipe_detail_ui(recipe_id: int, request: Request, session: Session = Depends(get_session)):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return HTMLResponse("レシピが見つかりません", status_code=404)
    return templates.TemplateResponse(
        "recipe_detail.html",
        {"request": request, "recipe": recipe},
    )

# ----------------------------
# レシピ保存（UI向け）
# ----------------------------

from app.models import Recipe, Ingredient
from app.schemas import RecipeCreate

@app.post("/save_recipe_ui", response_class=HTMLResponse)
def save_recipe_ui(
    request: Request,
    title: str = Form(...),
    steps: str = Form(...),
    ingredients: str = Form(""),
    image_url: str = Form(None),
    tags: List[str] = Form([]),
    session: Session = Depends(get_session),
    current_user: User = Depends(auth.get_current_user),
):
    current_user = get_current_user(request, session)
    if not current_user:
        return RedirectResponse(url="/login", status_code=303)
    """
    レシピをDBに保存するUI用ルート
    """
    recipe = Recipe(
        title=title,
        steps=steps,
        image_url=image_url,
        favorite=False,
        user_id=current_user.id
    )

    # 食材を登録（カンマ区切り）
    ing_list = [i.strip() for i in ingredients.split(",") if i.strip()]
    for ing_name in ing_list:
        db_ing = session.exec(select(Ingredient).where(Ingredient.name == ing_name)).first()
        if not db_ing:
            db_ing = Ingredient(name=ing_name)
        recipe.ingredients.append(db_ing)

    # タグを登録（カンマ区切り）
    for tag_name in tags:
        session_tag = session.exec(select(Tag).where(Tag.name == tag_name)).first()
        if session_tag:
            recipe.tags.append(session_tag)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    return templates.TemplateResponse(
        "recipe_saved.html",
        {"request": request, "recipe": recipe},
    )

@app.post("/recipes_ui/{recipe_id}/toggle_fav", response_class=HTMLResponse)
def toggle_favorite(recipe_id: int, request: Request, session: Session = Depends(get_session)):
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        return HTMLResponse("レシピが見つかりません", status_code=404)

    # ★を反転
    recipe.favorite = not recipe.favorite
    session.add(recipe)
    session.commit()
    session.refresh(recipe)

    # 一覧にリダイレクト
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/recipes_ui", status_code=303)

# タグ管理ページ
@app.get("/tags_ui", response_class=HTMLResponse)
def list_tags_ui(request: Request, session: Session = Depends(get_session)):
    tags = session.exec(select(Tag)).all()
    return templates.TemplateResponse(
        "tags_list.html",
        {"request": request, "tags": tags},
    )

# タグ追加
@app.post("/tags_ui/add", response_class=HTMLResponse)
def add_tag(name: str = Form(...), session: Session = Depends(get_session)):
    tag = Tag(name=name)
    session.add(tag)
    session.commit()
    return RedirectResponse(url="/tags_ui", status_code=303)

# タグ削除
@app.post("/tags_ui/{tag_id}/delete", response_class=HTMLResponse)
def delete_tag(tag_id: int, session: Session = Depends(get_session)):
    tag = session.get(Tag, tag_id)
    if tag:
        session.delete(tag)
        session.commit()
    return RedirectResponse(url="/tags_ui", status_code=303)