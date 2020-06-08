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

class Pv(Model):
    __tablename__ = 'pvs'

    pv_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    home_hub_id = Column(db.Integer, db.ForeignKey('home_hubs.home_hub_id', nullable=False))
    q_rated = Column(db.Float, nullable=False)
    is_active = Column(db.Boolean(False), nullable=False)
    is_archived = Column(db.Boolean(False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    home_hub = relationship('HomeHub', backref=db.backref('pvs'))
    pv_intervals = relationship('PvInterval', backref=db.backref('pvs'))

    def __repr__(self):
        return f'<Pv pv_id={self.pv_id} home_hub_id={self.home_hub_id} created_at={self.created_at}>'