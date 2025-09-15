# app/models.py
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime


class RecipeIngredientLink(SQLModel, table=True):
    """
    レシピと食材の中間テーブル（多対多関係を表現）
    """
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id", primary_key=True)
    ingredient_id: Optional[int] = Field(default=None, foreign_key="ingredient.id", primary_key=True)

class RecipeTag(SQLModel, table=True):
    """
    レシピとタグの中間テーブル（多対多関係を表現）
    """
    recipe_id: Optional[int] = Field(default=None, foreign_key="recipe.id", primary_key=True)
    tag_id: Optional[int] = Field(default=None, foreign_key="tag.id", primary_key=True)

class Recipe(SQLModel, table=True):
    """
    レシピ本体を保存するテーブル
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    steps: str
    image_url: Optional[str] = None
    favorite: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # ingredientsとの多対多関係
    ingredients: List["Ingredient"] = Relationship(back_populates="recipes", link_model=RecipeIngredientLink)

    tags: List["Tag"] = Relationship(back_populates="recipes", link_model=RecipeTag)


class Tag(SQLModel, table=True):
    """
    タグを保存するテーブル
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # recipesとの多対多関係
    recipes: List["Recipe"] = Relationship(back_populates="tags", link_model=RecipeTag)


class Ingredient(SQLModel, table=True):
    """
    食材を保存するテーブル
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    # recipesとの多対多関係
    recipes: List[Recipe] = Relationship(back_populates="ingredients", link_model=RecipeIngredientLink)

    