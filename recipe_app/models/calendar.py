from pydantic import BaseModel
from typing import Optional, List
from datetime import date
from .recipe import Recipe

class MealPlanBase(BaseModel):
    date: date
    meal_type: str  # breakfast, lunch, dinner, snack
    recipe_id: int

class MealPlanCreate(MealPlanBase):
    pass

class MealPlan(MealPlanBase):
    id: int

    class Config:
        orm_mode = True

class MealPlanWithRecipe(MealPlan):
    recipe: Recipe

class DailyMealPlan(BaseModel):
    date: date
    breakfast: Optional[Recipe] = None
    lunch: Optional[Recipe] = None
    dinner: Optional[Recipe] = None
    snacks: List[Recipe] = []

class WeeklyMealPlan(BaseModel):
    start_date: date
    end_date: date
    days: List[DailyMealPlan]