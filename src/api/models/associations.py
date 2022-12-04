from sqlalchemy import Column, Float, ForeignKey, CheckConstraint

from src.api.database import db


recipe_ingredients = db.Table(
    "recipe_ingredients",
    db.Model.metadata,
    Column(
        "recipe_id",
        ForeignKey("recipe.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    Column(
        "ingredient_id",
        ForeignKey("ingredient.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    ),
    Column(
        "unit_of_measure",
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"),
        nullable=False,
    ),
    Column("quantity", Float, nullable=False),
    CheckConstraint("quantity > 0"),
)
