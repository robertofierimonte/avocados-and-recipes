from marshmallow import fields

from src.api.database import ma
from src.api.models.recipe import Recipe, Ingredient, RecipeIngredients


class IngredientSchema(ma.SQLAlchemyAutoSchema):
    """Schema for an Ingredient."""

    class Meta:
        """Schema for an Ingredient."""

        model = Ingredient


class RecipeIngredientsSchema(ma.SQLAlchemyAutoSchema):
    """Schema for the RecipeIngredients table."""

    class Meta:
        """Schema for the RecipeIngredients table."""

        model = RecipeIngredients
        include_fk = True
        include_relationship = True

    ingredient = fields.Pluck(IngredientSchema, "name")


class RecipeSchema(ma.SQLAlchemyAutoSchema):
    """Schema for a Recipe."""

    class Meta:
        """Schema for a recipe."""

        model = Recipe
        include_relationsips = True

    ingredients = fields.Nested(
        RecipeIngredientsSchema,
        many=True,
        only=("ingredient", "quantity", "unit_of_measure"),
    )
