from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.pv import Pv
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

    home_hub_id = Column(db.Integer, 
                         autoincrement=True, 
                         primary_key=True, 
                         nullable=False)

    service_location_id = Column(db.Integer, 
                                 db.ForeignKey('service_locations.service_location_id'), 
                                 unique=True,
                                 nullable=False)
    market_id = Column(db.Integer, 
                       db.ForeignKey('markets.market_id'),
                       nullable=False)

    is_active = Column(db.Boolean(), 
                       default=False, 
                       nullable=False)

    is_archived = Column(db.Boolean(), 
                         default=False, 
                         nullable=False)

    created_at = Column(TIMESTAMP, 
                        default=datetime.utcnow,
                        nullable=False)

    updated_at = Column(TIMESTAMP, 
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow,
                        nullable=False)
    
    # Methods
    def __repr__(self):
        return f'<HomeHub home_hub_id={self.home_hub_id} service_location_id={self.service_location_id} created_at={self.created_at}>'

    # Relationships
    pv = relationship('Pv',
                      backref=db.backref('home_hub'),
                      uselist=False)

##########################
### MARSHMALLOW SCHEMA ###
##########################


class HomeHubSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HomeHub
        load_instance = True
        include_fk = True