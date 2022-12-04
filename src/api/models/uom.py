from datetime import datetime

from sqlalchemy import text, Float, ForeignKey, CheckConstraint
from sqlalchemy.schema import FetchedValue

from src.api.database import db, ma


class UOMConversion(db.Model):
    """Declarative model for the uom_conversion association table."""

    __tablename__ = "uom_conversion"
    uom_from = db.Column(
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"), nullable=False
    )
    uom_to = db.Column(
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"), nullable=False
    )
    factor = db.Column(Float, nullable=False)
    __table_args__ = (CheckConstraint("factor > 0"),)
    # Define a joint primary key
    __mapper_args__ = {"primary_key": [uom_from, uom_to]}
    # Define relationships between the association table and the relevant
    # entities
    _from = db.relationship(
        "UnitOfMeasure",
        back_populates="uoms_to",
        primaryjoin="UOMConversion.uom_from == UnitOfMeasure.name",
    )
    _to = db.relationship(
        "UnitOfMeasure",
        back_populates="uoms_from",
        primaryjoin="UOMConversion.uom_to == UnitOfMeasure.name",
    )


class UnitOfMeasure(db.Model):
    """Declarative model for a Unit of Measure."""

    __tablename__ = "unit_of_measure"
    name = db.Column(db.String, primary_key=True)
    name_long = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    updated_at = db.Column(
        db.DateTime,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"),
        server_onupdate=FetchedValue(),
    )
    uoms_from = db.relationship("UOMConversion", back_populates="_to")
    uoms_to = db.relationship("UOMConversion", back_populates="_from")


class UnitOfMeasureSchema(ma.SQLAlchemySchema):
    """Schema for a Unit of Measure."""

    class Meta:
        """Schema for a Unit of Measure."""

        model = UnitOfMeasure
