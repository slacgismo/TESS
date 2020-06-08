from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.service_location import ServiceLocation
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class HomeHub(Model):
    __tablename__ = 'home_hubs'

    home_hub_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    service_location_id = Column(db.Integer, db.ForeignKey('service_location.service_location_id', nullable=False))
    p_max = Column(db.Float, nullable=False)
    is_active = Column(db.Boolean(False), nullable=False)
    is_archived = Column(db.Boolean(False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    meter = relationship('Meter', backref=db.backref('pvs'))
    home_hub = relationship('HomeHub', backref=db.backref('pvs'))

    def __repr__(self):
        return f'<HomeHub home_hub_id={self.home_hub_id} service_location_id={self.service_location_id} created_at={self.created_at}>'