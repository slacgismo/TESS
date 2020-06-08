from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.meter import Meter
from web.models.home_hub import HomeHub
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class PvStateIn(Model):
    __tablename__ = 'pv_state_ins'

    pv_state_in_id = Column(TIMESTAMP, primary_key=True, nullable=False)
    pv_id = Column(db.Integer, db.ForeignKey('pvs.pv_id', nullable=False))
    e = Column(db.Float, nullable=False)
    qmtp = Column(db.Float, nullable=False)
    
    # Relationships
    pv = relationship('Pv', backref=db.backref('pvs'))
