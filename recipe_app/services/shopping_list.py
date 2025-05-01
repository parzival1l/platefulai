from typing import List, Dict, Any
from datetime import date, timedelta
from sqlalchemy.orm import Session
from collections import defaultdict

from database import Recipe, Ingredient, MealPlan
from models.shopping import ShoppingItem, ShoppingList, ShoppingListByCategory

class ShoppingListGenerator:
    """Service for generating shopping lists from meal plans"""

    def __init__(self, db: Session):
        """Initialize the shopping list generator"""
        self.db = db

    def generate_shopping_list(self, start_date: date, end_date: date) -> ShoppingList:
        """
        Generate a shopping list for the specified date range

        Args:
            start_date: Start date of the meal plan
            end_date: End date of the meal plan

        Returns:
            ShoppingList containing consolidated ingredients
        """
        # Get all meal plans for the specified date range
        meal_plans = self.db.query(MealPlan).filter(
            MealPlan.date >= start_date,
            MealPlan.date <= end_date
        ).all()

        # Extract all recipe IDs
        recipe_ids = [meal_plan.recipe_id for meal_plan in meal_plans]

        # Get all recipes
        recipes = self.db.query(Recipe).filter(Recipe.id.in_(recipe_ids)).all()

        # Create a mapping of recipe ID to name for reference
        recipe_names = {recipe.id: recipe.name for recipe in recipes}

        # Get all ingredients from these recipes
        ingredients_by_recipe = {}
        for recipe in recipes:
            ingredients_by_recipe[recipe.id] = recipe.ingredients

        # Consolidate ingredients
        consolidated_ingredients = self._consolidate_ingredients(
            ingredients_by_recipe, recipe_names
        )

        # Create shopping list
        return ShoppingList(
            start_date=start_date,
            end_date=end_date,
            items=consolidated_ingredients
        )

    def generate_categorized_shopping_list(
        self, start_date: date, end_date: date
    ) -> ShoppingListByCategory:
        """
        Generate a shopping list organized by category

        Args:
            start_date: Start date of the meal plan
            end_date: End date of the meal plan

        Returns:
            ShoppingListByCategory containing ingredients organized by category
        """
        # Get regular shopping list
        shopping_list = self.generate_shopping_list(start_date, end_date)

        # Categorize items
        categorized_items = self._categorize_ingredients(shopping_list.items)

        # Create categorized shopping list
        return ShoppingListByCategory(
            start_date=start_date,
            end_date=end_date,
            categories=categorized_items
        )

    def _consolidate_ingredients(
        self,
        ingredients_by_recipe: Dict[int, List[Ingredient]],
        recipe_names: Dict[int, str]
    ) -> List[ShoppingItem]:
        """
        Consolidate ingredients from multiple recipes

        Args:
            ingredients_by_recipe: Dict mapping recipe ID to list of ingredients
            recipe_names: Dict mapping recipe ID to recipe name

        Returns:
            List of consolidated ShoppingItems
        """
        # Create a dictionary to track consolidated ingredients
        # Key is (name, unit) to handle different units separately
        consolidated = {}

        # Process all ingredients
        for recipe_id, ingredients in ingredients_by_recipe.items():
            recipe_name = recipe_names[recipe_id]

            for ingredient in ingredients:
                key = (ingredient.name.lower(), ingredient.unit.lower())

                if key in consolidated:
                    # Update existing ingredient
                    consolidated[key]["amount"] += ingredient.amount
                    consolidated[key]["recipes"].add(recipe_name)
                else:
                    # Add new ingredient
                    consolidated[key] = {
                        "name": ingredient.name,
                        "amount": ingredient.amount,
                        "unit": ingredient.unit,
                        "recipes": {recipe_name}
                    }

        # Convert to ShoppingItem objects
        shopping_items = []
        for item_data in consolidated.values():
            shopping_items.append(
                ShoppingItem(
                    name=item_data["name"],
                    amount=item_data["amount"],
                    unit=item_data["unit"],
                    recipes=list(item_data["recipes"])
                )
            )

        # Sort by name
        shopping_items.sort(key=lambda x: x.name)

        return shopping_items

    def _categorize_ingredients(self, items: List[ShoppingItem]) -> Dict[str, List[ShoppingItem]]:
        """
        Categorize ingredients into food groups

        Args:
            items: List of ShoppingItems to categorize

        Returns:
            Dict mapping category names to lists of ShoppingItems
        """
        # Define categories and common ingredients in each
        categories = {
            "Produce": [
                "apple", "banana", "lettuce", "tomato", "onion", "garlic",
                "carrot", "potato", "cucumber", "pepper", "spinach", "kale",
                "broccoli", "cabbage", "celery", "mushroom", "fruit", "vegetable"
            ],
            "Meat & Seafood": [
                "beef", "chicken", "pork", "lamb", "turkey", "fish", "salmon",
                "tuna", "shrimp", "seafood", "meat", "steak", "bacon", "sausage"
            ],
            "Dairy & Eggs": [
                "milk", "cheese", "yogurt", "butter", "cream", "egg", "dairy"
            ],
            "Bakery": [
                "bread", "roll", "bun", "bagel", "tortilla", "pita", "pastry", "cake"
            ],
            "Grains & Pasta": [
                "rice", "pasta", "noodle", "cereal", "oat", "grain", "quinoa", "barley"
            ],
            "Canned Goods": [
                "can", "soup", "bean", "tomato sauce", "corn", "tuna"
            ],
            "Condiments & Spices": [
                "salt", "pepper", "spice", "herb", "sauce", "oil", "vinegar",
                "ketchup", "mustard", "mayonnaise", "dressing"
            ],
            "Snacks": [
                "chip", "crisp", "cracker", "nut", "snack", "cookie", "chocolate"
            ],
            "Beverages": [
                "water", "juice", "soda", "coffee", "tea", "wine", "beer", "drink"
            ]
        }

        # Initialize result dictionary with empty lists
        result = defaultdict(list)

        # Categorize each item
        for item in items:
            item_name = item.name.lower()

            # Check each category for matches
            assigned = False
            for category, keywords in categories.items():
                if any(keyword in item_name for keyword in keywords):
                    result[category].append(item)
                    assigned = True
                    break

            # If no category matched, put in "Other"
            if not assigned:
                result["Other"].append(item)

        # Convert defaultdict to regular dict
        return dict(result)