from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class IngredientBase(BaseModel):
    name: str
    amount: float
    unit: str
    usda_food_id: Optional[str] = None
    calories_per_unit: Optional[float] = None

class IngredientCreate(IngredientBase):
    pass

class Ingredient(IngredientBase):
    id: int
    recipe_id: int

    class Config:
        orm_mode = True

class RecipeBase(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: str
    servings: int = Field(gt=0)
    prep_time: Optional[int] = None  # minutes
    cook_time: Optional[int] = None  # minutes

class RecipeCreate(RecipeBase):
    ingredients: List[IngredientCreate]

class Recipe(RecipeBase):
    id: int
    created_at: datetime
    ingredients: List[Ingredient] = []

    class Config:
        orm_mode = True

class RecipeWithCalories(Recipe):
    total_calories: float
    calories_per_serving: float