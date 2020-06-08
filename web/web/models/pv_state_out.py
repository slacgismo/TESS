from datetime import datetime, timedelta
import enum
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

class Mode(enum.Enum):
   valid = 'valid'

class PvStateOut(Model):
    __tablename__ = 'pv_state_outs'

    pv_state_out_id = Column(TIMESTAMP, primary_key=True, nullable=False)
    pv_state_in_id = Column(TIMESTAMP, db.ForeignKey('pv_state_ins.pv_id', nullable=False))
    pv_id = Column(db.Integer, db.ForeignKey('pvs.pv_id', nullable=False))
    p_bid = Column(db.Float, nullable=False)
    q_bid = Column(db.Float, nullable=False)
    mode = Column(db.Enum(Mode), nullable=False)

    # Relationships
    pv = relationship('Pv', backref=db.backref('pvs'))
    pv_state_out = relationship('PvStateOut', backref=db.backref('pvs'), uselist=False)