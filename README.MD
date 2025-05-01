# Recipe Management App

A Python web application for managing recipes, planning meals, and generating shopping lists.

## Features

1. **Recipe Management**
   - Add recipes manually with ingredients and instructions
   - Store recipes in a database
   - Calculate calorie information using USDA Food Database

2. **Nutrition Analysis**
   - Connect to USDA API for ingredient nutrition data
   - Calculate calories per serving for recipes
   - Display nutrition information

3. **Recipe Catalog**
   - Browse and search saved recipes
   - View recipe details
   - Edit and delete recipes

4. **Meal Planning Calendar**
   - Weekly meal planning interface
   - Assign recipes to specific days/meals
   - View and manage weekly meal plan

5. **Shopping List Generator**
   - Compile ingredients from all recipes in meal plan
   - Consolidate and organize ingredients by category
   - Generate printable shopping list

## Technology Stack

- **Backend**: Python with FastAPI
- **Frontend**: HTML, CSS, JavaScript
- **Database**: SQLite
- **External APIs**: USDA FoodData Central API

## Project Structure

```
recipe_app/
├── main.py              # FastAPI application entry point
├── database.py          # Database connection and models
├── requirements.txt     # Python dependencies
├── routes/              # API endpoints
│   ├── __init__.py
│   ├── recipes.py       # Recipe CRUD operations
│   ├── nutrition.py     # USDA API integration
│   ├── calendar.py      # Meal planning endpoints
│   └── shopping.py      # Shopping list generation
├── models/              # Pydantic models
│   ├── __init__.py
│   ├── recipe.py        # Recipe models
│   ├── calendar.py      # Meal plan models
│   └── shopping.py      # Shopping list models
├── services/            # Business logic
│   ├── __init__.py
│   ├── usda_api.py      # USDA API client
│   ├── recipe_parser.py # Recipe link parser placeholder
│   └── shopping_list.py # Shopping list generator
└── static/              # Static files
    ├── css/
    │   └── main.css     # Custom styles
    ├── js/              # JavaScript files
    └── templates/       # HTML templates
        ├── base.html    # Base template
        ├── index.html   # Homepage
        ├── recipes/     # Recipe templates
        │   ├── index.html
        │   ├── detail.html
        │   ├── new.html
        │   └── edit.html
        ├── calendar/    # Calendar templates
        │   └── index.html
        └── shopping/    # Shopping list templates
            ├── list.html
            ├── categorized.html
            ├── print_list.html
            └── print_categorized.html
```

## Installation

1. Clone the repository
2. Create a virtual environment and activate it
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```
4. Get a USDA FoodData Central API key from [https://fdc.nal.usda.gov/api-key-signup.html](https://fdc.nal.usda.gov/api-key-signup.html)
5. Set the API key as an environment variable
   ```bash
   export USDA_API_KEY="your_api_key_here"  # On Windows: set USDA_API_KEY=your_api_key_here
   ```

## Usage

1. Start the application
   ```bash
   python main.py
   ```
2. Open a web browser and navigate to [http://localhost:8000](http://localhost:8000)
3. Use the following features:
   - Add recipes via the "Add Recipe" button
   - View and edit recipes in the recipe catalog
   - Plan meals using the calendar view
   - Generate shopping lists based on your meal plan

## Future Enhancements

- Recipe import from URLs using LLM parsing
- User authentication and multi-user support
- Export/import recipes in various formats
- Mobile application with offline support

## License

This project is licensed under the MIT License - see the LICENSE file for details.