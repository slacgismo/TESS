from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.address import Address, AddressSchema
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class ServiceLocation(Model):
    __tablename__ = 'service_locations'

    service_location_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    alternate_service_location_id = Column(db.String(64), unique=True)
    address_id = Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=False)
    map_location = Column(db.String(64), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False,default=datetime.utcnow, onupdate=datetime.utcnow)

    #one-to-one service location per address
    address = relationship('Address', backref=db.backref('service_locations'), uselist=False)

    def __repr__(self):
        return f'<ServiceLocation service_location_id={self.service_location_id} address_id={self.address_id}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################

class ServiceLocationSchema(SQLAlchemyAutoSchema):
    postal_code = fields.Method('get_postal_code', dump_only=True)
    address = fields.Nested(AddressSchema(), dump_only=True)

    class Meta:
        model = ServiceLocation
        load_instance = True
        include_fk = True
