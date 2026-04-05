from datetime import datetime

from pydantic import BaseModel, Field


class IngredientBase(BaseModel):
    name: str
    amount: float
    unit: str
    usda_food_id: str | None = None
    calories_per_unit: float | None = None


class IngredientCreate(IngredientBase):
    pass


class Ingredient(IngredientBase):
    id: int
    recipe_id: int

    class Config:
        orm_mode = True


class RecipeBase(BaseModel):
    name: str
    description: str | None = None
    instructions: str
    servings: int = Field(gt=0)
    prep_time: int | None = None  # minutes
    cook_time: int | None = None  # minutes


class RecipeCreate(RecipeBase):
    ingredients: list[IngredientCreate]


class Recipe(RecipeBase):
    id: int
    created_at: datetime
    ingredients: list[Ingredient] = []

    class Config:
        orm_mode = True


class RecipeWithCalories(Recipe):
    total_calories: float
    calories_per_serving: float
