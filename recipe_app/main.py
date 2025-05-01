from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
import uvicorn
import os

from database import create_tables, get_db
from routes import recipes, nutrition, calendar, shopping

# Create application directories if they don't exist
os.makedirs("recipe_app/static/css", exist_ok=True)
os.makedirs("recipe_app/static/js", exist_ok=True)
os.makedirs("recipe_app/static/templates", exist_ok=True)

# Get the absolute path to the project root directory (parent of recipe_app)
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(ROOT_DIR, "templates")

# Create FastAPI app
app = FastAPI(title="Recipe Management App")

# Mount static files
app.mount("/static", StaticFiles(directory="recipe_app/static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Create database tables
create_tables()

# Include routers
app.include_router(recipes.router, prefix="/recipes", tags=["recipes"])
app.include_router(nutrition.router, prefix="/nutrition", tags=["nutrition"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])
app.include_router(shopping.router, prefix="/shopping", tags=["shopping"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/debug", response_class=JSONResponse)
async def debug_info():
    """Debug information endpoint"""
    template_path = TEMPLATES_DIR
    template_files = os.listdir(template_path) if os.path.exists(template_path) else []

    static_files = {
        "css": os.listdir("recipe_app/static/css") if os.path.exists("recipe_app/static/css") else [],
        "js": os.listdir("recipe_app/static/js") if os.path.exists("recipe_app/static/js") else []
    }

    return {
        "status": "debug_mode",
        "app_info": {
            "title": app.title,
            "static_directory": "recipe_app/static",
            "templates_directory": template_path,
            "template_files": template_files,
            "static_files": static_files,
            "routes": [{"path": route.path, "name": route.name} for route in app.routes]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)