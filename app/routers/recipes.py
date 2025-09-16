# app/routers/recipes.py
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List

from app.database import get_session
from app.models import Recipe, Ingredient, RecipeIngredientLink
from app.schemas import RecipeCreate, RecipeRead

router = APIRouter(prefix="/recipes", tags=["recipes"])


@router.post("/", response_model=RecipeRead)
def create_recipe(recipe_data: RecipeCreate, session: Session = Depends(get_session)):
    """
    レシピを新規作成するAPI
    - RecipeCreateスキーマを受け取り、DBに保存
    - ingredientsは文字列リストで受け取り、Ingredientテーブルに登録
    """
    recipe = Recipe(title=recipe_data.title, steps=recipe_data.steps, favorite=recipe_data.favorite)

    # 食材を処理
    for ing_name in recipe_data.ingredients:
        # 既存の食材を検索
        statement = select(Ingredient).where(Ingredient.name == ing_name)
        db_ing = session.exec(statement).first()
        if not db_ing:
            db_ing = Ingredient(name=ing_name)
        recipe.ingredients.append(db_ing)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@router.get("/", response_model=List[RecipeRead])
def list_recipes(session: Session = Depends(get_session)):
    """
    保存されているレシピを一覧取得
    """
    recipes = session.exec(select(Recipe)).all()
    return recipes


@router.get("/{recipe_id}", response_model=RecipeRead)
def get_recipe(recipe_id: int, session: Session = Depends(get_session)):
    """
    指定IDのレシピを取得
    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")
    return recipe


@router.put("/{recipe_id}", response_model=RecipeRead)
def update_recipe(recipe_id: int, recipe_data: RecipeCreate, session: Session = Depends(get_session)):
    """
    レシピを更新するAPI
    - タイトル、手順、食材を置き換え
    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    recipe.title = recipe_data.title
    recipe.steps = recipe_data.steps
    recipe.favorite = recipe_data.favorite

    # 既存の食材リンクをリセット
    recipe.ingredients.clear()

    for ing_name in recipe_data.ingredients:
        statement = select(Ingredient).where(Ingredient.name == ing_name)
        db_ing = session.exec(statement).first()
        if not db_ing:
            db_ing = Ingredient(name=ing_name)
        recipe.ingredients.append(db_ing)

    session.add(recipe)
    session.commit()
    session.refresh(recipe)
    return recipe


@router.delete("/{recipe_id}")
def delete_recipe(recipe_id: int, session: Session = Depends(get_session)):
    """
    レシピを削除するAPI
    """
    recipe = session.get(Recipe, recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    session.delete(recipe)
    session.commit()
    return {"status": "success", "message": "Recipe deleted"}