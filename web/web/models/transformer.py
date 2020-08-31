import enum
from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text, func
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Transformer(Model):
    __tablename__ = 'transformers'
    transformer_id = Column(db.Integer,
                            primary_key=True,
                            autoincrement=True,
                            nullable=False)
    feeder = Column(db.String(45), nullable=False)
    capacity = Column(db.Integer, nullable=False)
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    created_at = Column(TIMESTAMP, server_default=func.now())


class TransformerSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Transformer
        load_instance = True
        include_fk = True
