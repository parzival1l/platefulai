from datetime import datetime

# Create SQLite database engine
from pathlib import Path as _Path

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

_DB_PATH = _Path(__file__).resolve().parent / "recipe_app.db"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{_DB_PATH}"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Create sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()


# Define models
class Recipe(Base):
    __tablename__ = "recipes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    instructions = Column(Text)
    servings = Column(Integer)
    prep_time = Column(Integer)  # in minutes
    cook_time = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.now)

    # Relationships
    ingredients = relationship("Ingredient", back_populates="recipe", cascade="all, delete")
    meal_plans = relationship("MealPlan", back_populates="recipe", cascade="all, delete")


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True)
    recipe_id = Column(Integer, ForeignKey("recipes.id"))
    name = Column(String, index=True)
    amount = Column(Float)
    unit = Column(String)
    usda_food_id = Column(String, nullable=True)
    calories_per_unit = Column(Float, nullable=True)

    # Relationships
    recipe = relationship("Recipe", back_populates="ingredients")


class MealPlan(Base):
    __tablename__ = "meal_plans"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, index=True)
    meal_type = Column(String)  # breakfast, lunch, dinner, snack
    recipe_id = Column(Integer, ForeignKey("recipes.id"))

    # Relationships
    recipe = relationship("Recipe", back_populates="meal_plans")


# Create all tables in the database
def create_tables():
    Base.metadata.create_all(bind=engine)


# Get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
