# app/schemas.py
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class IngredientBase(BaseModel):
    name: str


class IngredientRead(IngredientBase):
    id: int

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    title: str
    steps: str
    favorite: Optional[bool] = False


class RecipeCreate(RecipeBase):
    ingredients: List[str] = []  # 食材名リストで受け取る


class RecipeRead(RecipeBase):
    id: int
    image_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    ingredients: List[IngredientRead] = []

    class Config:
        orm_mode = True
