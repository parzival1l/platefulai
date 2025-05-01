from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import date, datetime, timedelta

from database import get_db, Recipe, MealPlan
from models.calendar import MealPlanCreate, WeeklyMealPlan, DailyMealPlan

router = APIRouter()
templates = Jinja2Templates(directory="static/templates")

@router.get("/", response_class=HTMLResponse)
async def show_calendar(
    request: Request,
    start_date: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Render the meal planning calendar

    Args:
        request: FastAPI request object
        start_date: Optional start date in YYYY-MM-DD format
        db: Database session

    Returns:
        HTML response with calendar view
    """
    # Parse start date or use current date
    if start_date:
        try:
            current_date = datetime.strptime(start_date, "%Y-%m-%d").date()
        except ValueError:
            current_date = date.today()
    else:
        current_date = date.today()

    # Find the Monday of the current week
    days_since_monday = current_date.weekday()
    monday = current_date - timedelta(days=days_since_monday)

    # Generate a week of dates
    week_dates = [monday + timedelta(days=i) for i in range(7)]
    start_date = week_dates[0]
    end_date = week_dates[-1]

    # Get all meal plans for the current week
    meal_plans = db.query(MealPlan).filter(
        MealPlan.date >= start_date,
        MealPlan.date <= end_date
    ).all()

    # Organize meal plans by date and meal type
    calendar_data = {}
    for d in week_dates:
        calendar_data[d] = {
            "breakfast": None,
            "lunch": None,
            "dinner": None,
            "snacks": []
        }

    for plan in meal_plans:
        recipe = db.query(Recipe).filter(Recipe.id == plan.recipe_id).first()

        if plan.meal_type == "snack":
            calendar_data[plan.date]["snacks"].append({
                "plan_id": plan.id,
                "recipe_id": plan.recipe_id,
                "recipe_name": recipe.name if recipe else "Unknown Recipe"
            })
        else:
            calendar_data[plan.date][plan.meal_type] = {
                "plan_id": plan.id,
                "recipe_id": plan.recipe_id,
                "recipe_name": recipe.name if recipe else "Unknown Recipe"
            }

    # Get all recipes for the dropdown
    recipes = db.query(Recipe).all()

    return templates.TemplateResponse(
        "calendar/index.html",
        {
            "request": request,
            "week_dates": week_dates,
            "calendar_data": calendar_data,
            "recipes": recipes,
            "prev_week": (start_date - timedelta(days=7)).isoformat(),
            "next_week": (start_date + timedelta(days=7)).isoformat(),
            "current_week_start": start_date.isoformat()
        }
    )

@router.post("/plan")
async def add_meal_plan(
    date: str = Form(...),
    meal_type: str = Form(...),
    recipe_id: int = Form(...),
    db: Session = Depends(get_db)
):
    """
    Add a new meal plan

    Args:
        date: Date in YYYY-MM-DD format
        meal_type: Type of meal (breakfast, lunch, dinner, snack)
        recipe_id: ID of the recipe to add
        db: Database session

    Returns:
        Redirect to calendar view
    """
    try:
        # Parse date
        plan_date = datetime.strptime(date, "%Y-%m-%d").date()

        # Verify recipe exists
        recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        # For breakfast, lunch, dinner: check if a plan already exists and replace it
        if meal_type in ["breakfast", "lunch", "dinner"]:
            existing_plan = db.query(MealPlan).filter(
                MealPlan.date == plan_date,
                MealPlan.meal_type == meal_type
            ).first()

            if existing_plan:
                existing_plan.recipe_id = recipe_id
                db.commit()
                return RedirectResponse(url=f"/calendar?start_date={date}", status_code=303)

        # Create new meal plan
        meal_plan = MealPlan(
            date=plan_date,
            meal_type=meal_type,
            recipe_id=recipe_id
        )
        db.add(meal_plan)
        db.commit()

        return RedirectResponse(url=f"/calendar?start_date={date}", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/plan/{plan_id}/delete")
async def delete_meal_plan(plan_id: int, redirect_date: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Delete a meal plan

    Args:
        plan_id: ID of the meal plan to delete
        redirect_date: Optional date to redirect to after deletion
        db: Database session

    Returns:
        Redirect to calendar view
    """
    plan = db.query(MealPlan).filter(MealPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Meal plan not found")

    # Remember the date for redirection
    plan_date = plan.date.isoformat()

    # Delete the plan
    db.delete(plan)
    db.commit()

    # Redirect to the calendar, either to the specified date or the plan's date
    redirect_to = redirect_date if redirect_date else plan_date
    return RedirectResponse(url=f"/calendar?start_date={redirect_to}", status_code=303)

@router.get("/api/weekly")
async def get_weekly_meal_plan(
    start_date: str,
    db: Session = Depends(get_db)
):
    """
    Get weekly meal plan data as JSON

    Args:
        start_date: Start date of the week in YYYY-MM-DD format
        db: Database session

    Returns:
        Weekly meal plan data
    """
    try:
        # Parse start date
        week_start = datetime.strptime(start_date, "%Y-%m-%d").date()
        week_end = week_start + timedelta(days=6)

        # Get all meal plans for the week
        meal_plans = db.query(MealPlan).filter(
            MealPlan.date >= week_start,
            MealPlan.date <= week_end
        ).all()

        # Organize by date
        daily_plans = {}
        for i in range(7):
            current_date = week_start + timedelta(days=i)
            daily_plans[current_date] = DailyMealPlan(
                date=current_date,
                breakfast=None,
                lunch=None,
                dinner=None,
                snacks=[]
            )

        # Fill in meal plans
        for plan in meal_plans:
            recipe = db.query(Recipe).filter(Recipe.id == plan.recipe_id).first()
            if not recipe:
                continue

            if plan.meal_type == "snack":
                daily_plans[plan.date].snacks.append(recipe)
            elif plan.meal_type == "breakfast":
                daily_plans[plan.date].breakfast = recipe
            elif plan.meal_type == "lunch":
                daily_plans[plan.date].lunch = recipe
            elif plan.meal_type == "dinner":
                daily_plans[plan.date].dinner = recipe

        # Convert to list for response
        days = [daily_plans[week_start + timedelta(days=i)] for i in range(7)]

        return WeeklyMealPlan(
            start_date=week_start,
            end_date=week_end,
            days=days
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))