from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError

from web.models.utility import Utility
from web.models.channel import Channel
from web.models.interval import Interval
from web.models.service_location import ServiceLocation, ServiceLocationSchema
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

# class Market(Model):
#     __tablename__ = 'markets'

#     market_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
#     utility_id = Column(db.Integer,
#                         db.ForeignKey('utilities.utility_id'),
#                         primary_key=True,
#                         nullable=False)
#     service_location_id = Column(
#         db.String(64),
#         db.ForeignKey('service_locations.service_location_id'),
#         primary_key=True,
#         nullable=False)

#     feeder = Column(db.String(45), nullable=False)
#     substation = Column(db.String(45), nullable=False)
#     meter_type = Column(db.Enum(MeterType), nullable=False)
#     is_active = Column(db.Boolean(False), nullable=False)
#     is_archived = Column(db.Boolean(False), nullable=False)
#     created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
#     updated_at = Column(TIMESTAMP,
#                         nullable=False,
#                         default=datetime.utcnow,
#                         onupdate=datetime.utcnow)

#     # Relationships
#     service_location = relationship('ServiceLocation',
#                                     backref=db.backref('meters'))
#     utility = relationship('Utility', backref=db.backref('meters'))
#     channels = relationship('Channel', backref=db.backref('meters'))
#     intervals = relationship('Interval', backref=db.backref('meters'))
