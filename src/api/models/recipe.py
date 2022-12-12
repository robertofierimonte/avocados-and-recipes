from sqlalchemy import text, CheckConstraint, ForeignKey
from sqlalchemy.schema import FetchedValue

from src.api.database import db


class Recipe(db.Model):
    """Declarative model for a Recipe."""

    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    method = db.Column(db.String)
    author = db.Column(db.String)
    book = db.Column(db.String)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = db.Column(
        db.DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )
    ingredients = db.relationship("RecipeIngredients", back_populates="recipe")


class Ingredient(db.Model):
    """Declarative model for an Ingredient."""

    __tablename__ = "ingredient"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    brand = db.Column(db.String)
    ref_unit_of_measure = db.Column(db.String, nullable=False)
    ref_quantity = db.Column(db.Float, default=1)
    ref_price = db.Column(db.Float, default=0)
    available = db.Column(db.Boolean, default=True)
    created_at = db.Column(
        db.DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )
    __table_args__ = (
        CheckConstraint("ref_quantity > 0"),
        CheckConstraint("ref_price >= 0"),
    )
    recipes = db.relationship("RecipeIngredients", back_populates="ingredient")


class RecipeIngredients(db.Model):
    """Declarative model for the recipe_ingredients association table."""

    __tablename__ = "recipe_ingredients"
    recipe_id = db.Column(
        db.Integer,
        ForeignKey("recipe.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    ingredient_id = db.Column(
        db.Integer,
        ForeignKey("ingredient.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    )
    unit_of_measure = db.Column(
        db.String,
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"),
        nullable=False,
    )
    quantity = db.Column(db.Float, nullable=False)
    __table_args__ = (CheckConstraint("quantity > 0"),)
    # Define relationships between the association table and the relevant
    # entities
    ingredient = db.relationship("Ingredient", back_populates="recipes")
    recipe = db.relationship("Recipe", back_populates="ingredients")
