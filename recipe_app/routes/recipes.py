from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from database import get_db, Recipe, Ingredient
from models.recipe import RecipeCreate, Recipe as RecipeModel, RecipeWithCalories
from services.usda_api import USDAApiClient

router = APIRouter()
templates = Jinja2Templates(directory="static/templates")
usda_client = USDAApiClient()

@router.get("/", response_class=HTMLResponse)
async def list_recipes(request: Request, db: Session = Depends(get_db)):
    """Render the recipe catalog page"""
    recipes = db.query(Recipe).all()
    return templates.TemplateResponse(
        "recipes/index.html",
        {"request": request, "recipes": recipes}
    )

@router.get("/new", response_class=HTMLResponse)
async def new_recipe_form(request: Request):
    """Render the new recipe form"""
    return templates.TemplateResponse(
        "recipes/new.html",
        {"request": request}
    )

@router.post("/")
async def create_recipe(
    name: str = Form(...),
    description: str = Form(None),
    instructions: str = Form(...),
    servings: int = Form(...),
    prep_time: int = Form(None),
    cook_time: int = Form(None),
    ingredients_json: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new recipe"""
    try:
        # Parse ingredients from JSON
        ingredients_data = json.loads(ingredients_json)

        # Create recipe in database
        db_recipe = Recipe(
            name=name,
            description=description,
            instructions=instructions,
            servings=servings,
            prep_time=prep_time,
            cook_time=cook_time
        )
        db.add(db_recipe)
        db.flush()  # Get the recipe ID

        # Add ingredients
        for ing_data in ingredients_data:
            db_ingredient = Ingredient(
                recipe_id=db_recipe.id,
                name=ing_data["name"],
                amount=ing_data["amount"],
                unit=ing_data["unit"],
                usda_food_id=ing_data.get("usda_food_id"),
                calories_per_unit=ing_data.get("calories_per_unit")
            )
            db.add(db_ingredient)

        db.commit()

        # Redirect to recipe detail page
        return RedirectResponse(url=f"/recipes/{db_recipe.id}", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{recipe_id}", response_class=HTMLResponse)
async def get_recipe(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    """Render the recipe detail page"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Calculate total calories if USDA food IDs are available
    total_calories = 0
    for ingredient in recipe.ingredients:
        if ingredient.calories_per_unit:
            total_calories += ingredient.amount * ingredient.calories_per_unit

    calories_per_serving = total_calories / recipe.servings if recipe.servings > 0 else 0

    return templates.TemplateResponse(
        "recipes/detail.html",
        {
            "request": request,
            "recipe": recipe,
            "total_calories": total_calories,
            "calories_per_serving": calories_per_serving
        }
    )

@router.get("/{recipe_id}/edit", response_class=HTMLResponse)
async def edit_recipe_form(request: Request, recipe_id: int, db: Session = Depends(get_db)):
    """Render the edit recipe form"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return templates.TemplateResponse(
        "recipes/edit.html",
        {"request": request, "recipe": recipe}
    )

@router.post("/{recipe_id}")
async def update_recipe(
    recipe_id: int,
    name: str = Form(...),
    description: str = Form(None),
    instructions: str = Form(...),
    servings: int = Form(...),
    prep_time: int = Form(None),
    cook_time: int = Form(None),
    ingredients_json: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update an existing recipe"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    try:
        # Update recipe fields
        recipe.name = name
        recipe.description = description
        recipe.instructions = instructions
        recipe.servings = servings
        recipe.prep_time = prep_time
        recipe.cook_time = cook_time

        # Delete existing ingredients
        db.query(Ingredient).filter(Ingredient.recipe_id == recipe_id).delete()

        # Parse ingredients from JSON
        ingredients_data = json.loads(ingredients_json)

        # Add updated ingredients
        for ing_data in ingredients_data:
            db_ingredient = Ingredient(
                recipe_id=recipe_id,
                name=ing_data["name"],
                amount=ing_data["amount"],
                unit=ing_data["unit"],
                usda_food_id=ing_data.get("usda_food_id"),
                calories_per_unit=ing_data.get("calories_per_unit")
            )
            db.add(db_ingredient)

        db.commit()

        # Redirect to recipe detail page
        return RedirectResponse(url=f"/recipes/{recipe_id}", status_code=303)

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{recipe_id}/delete")
async def delete_recipe(recipe_id: int, db: Session = Depends(get_db)):
    """Delete a recipe"""
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    db.delete(recipe)
    db.commit()

    # Redirect to recipe list
    return RedirectResponse(url="/recipes", status_code=303)

@router.get("/search")
async def search_recipes(request: Request, q: str, db: Session = Depends(get_db)):
    """Search for recipes by name"""
    recipes = db.query(Recipe).filter(Recipe.name.ilike(f"%{q}%")).all()
    return templates.TemplateResponse(
        "recipes/index.html",
        {"request": request, "recipes": recipes, "search_query": q}
    )

@router.get("/api/list")
async def api_list_recipes(db: Session = Depends(get_db)):
    """API endpoint to list all recipes (for AJAX calls)"""
    recipes = db.query(Recipe).all()
    return [{"id": r.id, "name": r.name} for r in recipes]