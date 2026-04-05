from pathlib import Path

import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from recipe_app.database import create_tables
from recipe_app.routes import calendar, nutrition, recipes, shopping

# Resolve paths relative to this file so they work regardless of CWD
_PKG_DIR = Path(__file__).resolve().parent
_ROOT_DIR = _PKG_DIR.parent
_STATIC_DIR = _PKG_DIR / "static"
_TEMPLATES_DIR = _ROOT_DIR / "templates"

# Create FastAPI app
app = FastAPI(title="Plateful AI")

# Mount static files
app.mount("/static", StaticFiles(directory=str(_STATIC_DIR)), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory=str(_TEMPLATES_DIR))

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
    return templates.TemplateResponse(request, "index.html")


@app.get("/debug", response_class=JSONResponse)
async def debug_info():
    """Debug information endpoint"""
    template_files = list(_TEMPLATES_DIR.iterdir()) if _TEMPLATES_DIR.exists() else []

    css_dir = _STATIC_DIR / "css"
    js_dir = _STATIC_DIR / "js"

    return {
        "status": "debug_mode",
        "app_info": {
            "title": app.title,
            "static_directory": str(_STATIC_DIR),
            "templates_directory": str(_TEMPLATES_DIR),
            "template_files": [f.name for f in template_files],
            "static_files": {
                "css": [f.name for f in css_dir.iterdir()] if css_dir.exists() else [],
                "js": [f.name for f in js_dir.iterdir()] if js_dir.exists() else [],
            },
            "routes": [{"path": route.path, "name": route.name} for route in app.routes],
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8081, reload=True)
