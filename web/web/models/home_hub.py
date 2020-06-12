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
    service_location_id = Column(db.Integer, db.ForeignKey('service_locations.service_location_id'), nullable=False)
    is_active = Column(db.Boolean(False), nullable=False)
    is_archived = Column(db.Boolean(False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    service_location = relationship('ServiceLocation', backref=db.backref('home_hubs'), uselist=False)

    def __repr__(self):
        return f'<HomeHub home_hub_id={self.home_hub_id} service_location_id={self.service_location_id} created_at={self.created_at}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################

class HomeHubSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HomeHub
        load_instance = True
        include_fk = True