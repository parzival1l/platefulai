from datetime import date

from pydantic import BaseModel


class ShoppingItem(BaseModel):
    name: str
    amount: float
    unit: str
    recipes: list[str]  # List of recipe names using this ingredient


class ShoppingList(BaseModel):
    start_date: date
    end_date: date
    items: list[ShoppingItem]


class ShoppingListByCategory(BaseModel):
    start_date: date
    end_date: date
    categories: dict[str, list[ShoppingItem]]  # Category -> List of items
