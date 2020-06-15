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

    service_location_id = Column(db.Integer,
                                 primary_key=True, 
                                 autoincrement=True, 
                                 nullable=False)

    alternate_service_location_id = Column(db.String(64), 
                                           unique=True)

    address_id = Column(db.Integer,
                        db.ForeignKey('addresses.address_id'),
                        nullable=False)

    map_location = Column(db.String(64),
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

    #one-to-one service location per address
    address = relationship('Address',
                           backref=db.backref('service_locations'),
                           uselist=False)

    def __repr__(self):
        return f'<ServiceLocation service_location_id={self.service_location_id} address_id={self.address_id}>'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class ServiceLocationSchema(SQLAlchemyAutoSchema):
    address = fields.Nested(AddressSchema(),
                            dump_only=True)

    class Meta:
        model = ServiceLocation
        load_instance = True
        include_fk = True
