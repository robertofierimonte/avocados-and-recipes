from datetime import datetime

from sqlalchemy import text, Float, ForeignKey, CheckConstraint, Column
from sqlalchemy.schema import FetchedValue

from src.api.database import db, ma


uom_conversion = db.Table(
    "uom_conversion",
    db.Model.metadata,
    Column(
        "uom_from",
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column(
        "uom_to",
        ForeignKey("unit_of_measure.name", onupdate="CASCADE"),
        nullable=False,
        primary_key=True,
    ),
    Column("factor", Float, nullable=False),
    CheckConstraint("factor > 0"),
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
    uoms_to = db.relationship(
        "UnitOfMeasure",
        secondary="uom_conversion",
        primaryjoin=name == uom_conversion.c.uom_from,
        secondaryjoin=name == uom_conversion.c.uom_to,
        back_populates="uoms_to",
    )


class UnitOfMeasureSchema(ma.SQLAlchemySchema):
    """Schema for a Unit of Measure."""

    class Meta:
        """Schema for a Unit of Measure."""

        model = UnitOfMeasure
