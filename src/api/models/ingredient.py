from datetime import datetime

from sqlalchemy import text, CheckConstraint
from sqlalchemy.schema import FetchedValue

from src.api.database import db, ma


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


class IngredientSchema(ma.SQLAlchemySchema):
    """Schema for an Ingredient."""

    class Meta:
        """Schema for an Ingredient."""

        model = Ingredient
