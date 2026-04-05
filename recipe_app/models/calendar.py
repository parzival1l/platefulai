from datetime import date

from pydantic import BaseModel

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
    breakfast: Recipe | None = None
    lunch: Recipe | None = None
    dinner: Recipe | None = None
    snacks: list[Recipe] = []


class WeeklyMealPlan(BaseModel):
    start_date: date
    end_date: date
    days: list[DailyMealPlan]
