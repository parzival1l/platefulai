from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime, timedelta

from database import get_db
from services.shopping_list import ShoppingListGenerator

router = APIRouter()
templates = Jinja2Templates(directory="static/templates")

@router.get("/", response_class=HTMLResponse)
async def show_shopping_list(
    request: Request,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    categorized: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Render the shopping list page

    Args:
        request: FastAPI request object
        start_date: Optional start date in YYYY-MM-DD format
        end_date: Optional end date in YYYY-MM-DD format
        categorized: Whether to categorize ingredients
        db: Database session

    Returns:
        HTML response with shopping list
    """
    # If no dates provided, default to current week
    if not start_date or not end_date:
        # Find the Monday of the current week
        current_date = date.today()
        days_since_monday = current_date.weekday()
        monday = current_date - timedelta(days=days_since_monday)

        # Default to current week
        start_date_obj = monday
        end_date_obj = monday + timedelta(days=6)
    else:
        # Parse provided dates
        try:
            start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
            end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format")

    # Get shopping list
    generator = ShoppingListGenerator(db)

    if categorized:
        shopping_list = generator.generate_categorized_shopping_list(
            start_date_obj, end_date_obj
        )

        return templates.TemplateResponse(
            "shopping/categorized.html",
            {
                "request": request,
                "shopping_list": shopping_list,
                "start_date": start_date_obj.isoformat(),
                "end_date": end_date_obj.isoformat()
            }
        )
    else:
        shopping_list = generator.generate_shopping_list(
            start_date_obj, end_date_obj
        )

        return templates.TemplateResponse(
            "shopping/list.html",
            {
                "request": request,
                "shopping_list": shopping_list,
                "start_date": start_date_obj.isoformat(),
                "end_date": end_date_obj.isoformat()
            }
        )

@router.get("/api/list")
async def get_shopping_list(
    start_date: str,
    end_date: str,
    categorized: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get shopping list data as JSON

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        categorized: Whether to categorize ingredients
        db: Database session

    Returns:
        Shopping list data
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Get shopping list
        generator = ShoppingListGenerator(db)

        if categorized:
            return generator.generate_categorized_shopping_list(
                start_date_obj, end_date_obj
            )
        else:
            return generator.generate_shopping_list(
                start_date_obj, end_date_obj
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/print", response_class=HTMLResponse)
async def print_shopping_list(
    request: Request,
    start_date: str,
    end_date: str,
    categorized: bool = Query(True),
    db: Session = Depends(get_db)
):
    """
    Render a printable shopping list

    Args:
        request: FastAPI request object
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        categorized: Whether to categorize ingredients
        db: Database session

    Returns:
        HTML response with printable shopping list
    """
    try:
        # Parse dates
        start_date_obj = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date_obj = datetime.strptime(end_date, "%Y-%m-%d").date()

        # Get shopping list
        generator = ShoppingListGenerator(db)

        if categorized:
            shopping_list = generator.generate_categorized_shopping_list(
                start_date_obj, end_date_obj
            )

            return templates.TemplateResponse(
                "shopping/print_categorized.html",
                {
                    "request": request,
                    "shopping_list": shopping_list,
                    "start_date": start_date_obj,
                    "end_date": end_date_obj
                }
            )
        else:
            shopping_list = generator.generate_shopping_list(
                start_date_obj, end_date_obj
            )

            return templates.TemplateResponse(
                "shopping/print_list.html",
                {
                    "request": request,
                    "shopping_list": shopping_list,
                    "start_date": start_date_obj,
                    "end_date": end_date_obj
                }
            )

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")