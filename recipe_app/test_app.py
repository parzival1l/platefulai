from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

# Create FastAPI app
app = FastAPI(title="Test App")

# Create templates directory if it doesn't exist
os.makedirs("templates", exist_ok=True)

# Create a simple HTML template
with open("templates/test.html", "w") as f:
    f.write("""
<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
        .container { max-width: 800px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }
        h1 { color: #333; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Test Page</h1>
        <p>If you can see this page, your FastAPI server is working correctly!</p>
    </div>
</body>
</html>
    """)

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Render the test page"""
    return templates.TemplateResponse("test.html", {"request": request})

@app.get("/api/test")
async def test_api():
    """Simple API endpoint for testing"""
    return {"message": "API is working!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8082)