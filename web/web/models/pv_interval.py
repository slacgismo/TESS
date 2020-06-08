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

class Status(enum.Enum):
   VALID = 'valid'
   INVALID = 'invalid'

class PvInterval(Model):
    __tablename__ = 'pv_intervals'

    pv_interval_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    pv_id = Column(db.Integer, db.ForeignKey('pvs.pv_id', nullable=False))
    rate_id = Column(db.Integer, db.ForeignKey('rates.rate_id'), nullable=False) 
    status = Column(db.Enum(Status), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    e = Column(db.Float, nullable=False)
    qmtp = Column(db.Float, nullable=False)
    
    # Relationships
    rate = relationship('Rate', backref=db.backref('pv_intervals'))

    @staticmethod
    def get_interval_coverage(interval_id_list):
        '''Takes in list of meter interval ids, 
            returns list of tuples for start and end times in ISO8601 format'''

        selected_intervals = PvInterval.query.filter(PvInterval.pv_interval_id.in_(interval_id_list)).all()
        start_end_tuples_list = []

        for pv_interval in selected_intervals:
            start_end_tuples_list.append((pv_interval.start_time, pv_interval.end_time))

        return start_end_tuples_list

    def __repr__(self):
        return f'<PvInterval pv_interval_id={self.pv_interval_id} pv_id={self.pv_id} end_time={self.end_time} e={self.e}>'