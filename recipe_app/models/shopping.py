from pydantic import BaseModel
from typing import List, Dict
from datetime import date

class ShoppingItem(BaseModel):
    name: str
    amount: float
    unit: str
    recipes: List[str]  # List of recipe names using this ingredient

class ShoppingList(BaseModel):
    start_date: date
    end_date: date
    items: List[ShoppingItem]

class ShoppingListByCategory(BaseModel):
    start_date: date
    end_date: date
    categories: Dict[str, List[ShoppingItem]]  # Category -> List of items