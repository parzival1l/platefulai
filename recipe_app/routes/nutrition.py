from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from database import get_db, Recipe, Ingredient
from services.usda_api import USDAApiClient

router = APIRouter()
usda_client = USDAApiClient()

@router.get("/search")
async def search_usda_foods(query: str, page_size: int = Query(10, le=50)):
    """
    Search for foods in the USDA database

    Args:
        query: Search term
        page_size: Number of results to return (max 50)

    Returns:
        Search results from USDA API
    """
    try:
        results = usda_client.search_foods(query, page_size)

        # Extract relevant information
        foods = []
        if "foods" in results:
            for food in results["foods"]:
                foods.append({
                    "id": food.get("fdcId"),
                    "description": food.get("description"),
                    "brand": food.get("brandOwner", ""),
                    "category": food.get("foodCategory", ""),
                    "nutrients": [
                        {
                            "id": n.get("nutrientId"),
                            "name": n.get("nutrientName"),
                            "amount": n.get("value"),
                            "unit": n.get("unitName")
                        }
                        for n in food.get("foodNutrients", [])
                        if n.get("nutrientId") in [1008, 1003, 1004, 1005]  # Calories, Protein, Fat, Carbs
                    ]
                })

        return {"foods": foods, "total_hits": results.get("totalHits", 0)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/food/{food_id}")
async def get_food_nutrients(food_id: str):
    """
    Get detailed nutrient information for a specific food

    Args:
        food_id: USDA FoodData Central ID

    Returns:
        Nutrient information for the specified food
    """
    try:
        food_data = usda_client.get_food_details(food_id)

        # Extract calories
        calories = None
        for nutrient in food_data.get("foodNutrients", []):
            if nutrient.get("nutrient", {}).get("id") == 1008:  # Energy (calories)
                calories = nutrient.get("amount")
                break

        return {
            "id": food_data.get("fdcId"),
            "description": food_data.get("description"),
            "calories_per_100g": calories,
            "nutrients": [
                {
                    "id": n.get("nutrient", {}).get("id"),
                    "name": n.get("nutrient", {}).get("name"),
                    "amount": n.get("amount"),
                    "unit": n.get("nutrient", {}).get("unitName")
                }
                for n in food_data.get("foodNutrients", [])
                if n.get("amount") is not None
            ]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/calculate/{recipe_id}")
async def calculate_recipe_nutrition(recipe_id: int, db: Session = Depends(get_db)):
    """
    Calculate nutrition information for a recipe

    Args:
        recipe_id: ID of the recipe

    Returns:
        Nutrition summary for the recipe
    """
    recipe = db.query(Recipe).filter(Recipe.id == recipe_id).first()
    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    # Calculate total calories
    total_calories = 0
    ingredients_with_calories = []

    for ingredient in recipe.ingredients:
        calories = None

        # If we already have calories info, use it
        if ingredient.calories_per_unit is not None:
            calories = ingredient.amount * ingredient.calories_per_unit

        # Otherwise, try to get from USDA API if we have a food ID
        elif ingredient.usda_food_id:
            try:
                calories_per_unit = usda_client.calculate_calories(
                    ingredient.usda_food_id,
                    1.0,
                    ingredient.unit
                )
                if calories_per_unit:
                    calories = calories_per_unit * ingredient.amount

                    # Update the ingredient with the calories info
                    ingredient.calories_per_unit = calories_per_unit
                    db.commit()
            except Exception:
                pass  # Skip if API call fails

        ingredients_with_calories.append({
            "id": ingredient.id,
            "name": ingredient.name,
            "amount": ingredient.amount,
            "unit": ingredient.unit,
            "calories": calories
        })

        if calories:
            total_calories += calories

    # Calculate calories per serving
    calories_per_serving = total_calories / recipe.servings if recipe.servings > 0 else 0

    return {
        "recipe_id": recipe_id,
        "recipe_name": recipe.name,
        "total_calories": total_calories,
        "calories_per_serving": calories_per_serving,
        "servings": recipe.servings,
        "ingredients": ingredients_with_calories
    }

@router.post("/update_ingredient_nutrition")
async def update_ingredient_nutrition(
    ingredient_id: int,
    usda_food_id: str,
    db: Session = Depends(get_db)
):
    """
    Update an ingredient with nutrition information from USDA API

    Args:
        ingredient_id: ID of the ingredient to update
        usda_food_id: USDA FoodData Central ID

    Returns:
        Updated ingredient information
    """
    ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_id).first()
    if not ingredient:
        raise HTTPException(status_code=404, detail="Ingredient not found")

    try:
        # Calculate calories per unit
        calories_per_unit = usda_client.calculate_calories(
            usda_food_id,
            1.0,
            ingredient.unit
        )

        if calories_per_unit is None:
            raise HTTPException(
                status_code=400,
                detail="Could not calculate calories for this ingredient"
            )

        # Update ingredient
        ingredient.usda_food_id = usda_food_id
        ingredient.calories_per_unit = calories_per_unit
        db.commit()

        return {
            "id": ingredient.id,
            "name": ingredient.name,
            "usda_food_id": ingredient.usda_food_id,
            "calories_per_unit": ingredient.calories_per_unit,
            "total_calories": ingredient.calories_per_unit * ingredient.amount
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))