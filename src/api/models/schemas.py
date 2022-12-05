from marshmallow_sqlalchemy import auto_field

from src.api.database import ma
from src.api.models.recipe import Recipe, Ingredient


class IngredientSchema(ma.SQLAlchemyAutoSchema):
    """Schema for an Ingredient."""

    class Meta:
        """Schema for an Ingredient."""

        model = Ingredient


class RecipeSchema(ma.SQLAlchemyAutoSchema):
    """Schema for a Recipe."""

    class Meta:
        """Schema for a recipe."""

        model = Recipe
