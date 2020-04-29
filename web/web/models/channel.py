from web.models.meter import Meter
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class Channel(Model):

    __tablename__ = 'channels'

    channel_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = Column(db.String(64), nullable=False)
    utility_id = Column(db.Integer, nullable=False)
    service_location_id = Column(db.String(64), nullable=False)
    setting = Column(db.Integer, nullable = False) 
    channel_type = Column(db.String(64), nullable=False)
    # created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    # updated_at = Column(TIMESTAMP, nullable=False,default=datetime.utcnow, onupdate=datetime.utcnow)

    #composite foreign key to meter
    __table_args__ = (
        ForeignKeyConstraint(
            [meter_id, utility_id, service_location_id],
            [Meter.meter_id, Meter.utility_id, Meter.service_location_id]
        ), 
        {}
    )

    #many-to-one channels per meter
    meter = relationship('Meter', backref=db.backref('channels'))

    def __repr__(self):
        return f'<Channel channel_id={self.channel_id} meter_id={self.meter_id} channel_type={self.channel_type}>'