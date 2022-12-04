from datetime import datetime

from sqlalchemy import text, CheckConstraint, ForeignKey, Float
from sqlalchemy.schema import FetchedValue

from src.api.database import db, ma


class RecipeIngredients(db.Model):
    """Declarative model for the recipe_ingredients association table."""

    __tablename__ = "recipe_ingredients"
    recipe_id = db.Column(
        ForeignKey("recipe.id", ondelete="CASCADE", onupdate="CASCADE"), nullable=False
    )
    ingredient_id = db.Column(
        ForeignKey("ingredient.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    unit_of_measure = db.Column(
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"), nullable=False
    )
    quantity = db.Column(Float, nullable=False)
    __table_args__ = (CheckConstraint("quantity > 0"),)
    # Define a joint primary key
    __mapper_args__ = {"primary_key": [recipe_id, ingredient_id]}
    # Define relationships between the association table and the relevant
    # entities
    ingredient = db.relationship("Ingredient", back_populates="recipes")
    recipe = db.relationship("Recipe", back_populates="ingredients")


class Recipe(db.Model):
    """Declarative model for a Recipe."""

    __tablename__ = "recipe"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    method = db.Column(db.String)
    author = db.Column(db.String)
    book = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(
        db.DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )
    ingredients = db.relationship("RecipeIngredients", back_populates="recipe")


class RecipeSchema(ma.SQLAlchemySchema):
    """Schema for a Recipe."""

    class Meta:
        """Schema for a recipe."""

        schema = Recipe


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
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
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


class IngredientSchema(ma.SQLAlchemySchema):
    """Schema for an Ingredient."""

    class Meta:
        """Schema for an Ingredient."""

        model = Ingredient
