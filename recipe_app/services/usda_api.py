import requests
import os
from typing import Dict, List, Optional, Any

class USDAApiClient:
    """Client for interacting with the USDA FoodData Central API"""

    BASE_URL = "https://api.nal.usda.gov/fdc/v1"

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the USDA API client"""
        self.api_key = api_key or os.getenv("USDA_API_KEY", "DEMO_KEY")

    def search_foods(self, query: str, page_size: int = 10) -> Dict[str, Any]:
        """
        Search for foods matching the query

        Args:
            query: The search term
            page_size: Number of results to return

        Returns:
            Dict containing search results
        """
        endpoint = f"{self.BASE_URL}/foods/search"
        params = {
            "api_key": self.api_key,
            "query": query,
            "pageSize": page_size,
            "dataType": ["Foundation", "SR Legacy"]  # Use standard reference data
        }

        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_food_details(self, food_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific food

        Args:
            food_id: The USDA FoodData Central ID

        Returns:
            Dict containing food details
        """
        endpoint = f"{self.BASE_URL}/food/{food_id}"
        params = {"api_key": self.api_key}

        response = requests.get(endpoint, params=params)
        response.raise_for_status()
        return response.json()

    def get_nutrient_data(self, food_id: str, nutrient_id: int = 1008) -> Optional[float]:
        """
        Get specific nutrient data for a food
        Default nutrient_id 1008 is for energy (calories)

        Args:
            food_id: The USDA FoodData Central ID
            nutrient_id: ID of the nutrient to retrieve

        Returns:
            Nutrient value or None if not found
        """
        food_data = self.get_food_details(food_id)

        # Look for the specified nutrient in the food data
        if "foodNutrients" in food_data:
            for nutrient in food_data["foodNutrients"]:
                if nutrient.get("nutrient", {}).get("id") == nutrient_id:
                    return nutrient.get("amount")

        return None

    def calculate_calories(self, food_id: str, amount: float, unit: str) -> Optional[float]:
        """
        Calculate calories for the specified amount of food

        Args:
            food_id: The USDA FoodData Central ID
            amount: The amount of the ingredient
            unit: The unit of measurement

        Returns:
            Calories or None if calculation fails
        """
        # Get calories per 100g (standard reference amount)
        calories_per_100g = self.get_nutrient_data(food_id)

        if calories_per_100g is None:
            return None

        # Convert amount to grams based on unit
        # This is a simplified conversion and would need to be expanded
        # with a more comprehensive unit conversion system
        grams = self._convert_to_grams(amount, unit)

        if grams is None:
            return None

        # Calculate calories for the specified amount
        return (calories_per_100g / 100) * grams

    def _convert_to_grams(self, amount: float, unit: str) -> Optional[float]:
        """
        Convert an amount from the given unit to grams

        Args:
            amount: The amount to convert
            unit: The unit to convert from

        Returns:
            Equivalent amount in grams or None if conversion not possible
        """
        # Simple conversion table (would need to be expanded)
        conversions = {
            "g": 1,
            "kg": 1000,
            "oz": 28.35,
            "lb": 453.592,
            "cup": 240,  # Rough estimate, depends on ingredient
            "tbsp": 15,
            "tsp": 5,
            "ml": 1,     # Assuming water density for liquids
            "l": 1000,
        }

        unit = unit.lower()
        if unit in conversions:
            return amount * conversions[unit]

        return None