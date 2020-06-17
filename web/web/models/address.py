from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Address(Model):
    __tablename__ = 'addresses'

    address_id = Column(db.Integer,
                        autoincrement=True,
                        primary_key=True,
                        nullable=False)

    address = Column(db.String(100), 
                     nullable=False)

    address2 = Column(db.String(64))

    district = Column(db.String(64))

    city = Column(db.String(100), 
                  nullable=False)

    country = Column(db.String(100), 
                     nullable=False)

    postal_code = Column(db.String(64), 
                         nullable=False)

    phone = Column(db.String(64))

    created_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow)
                        
    updated_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Address address_id={self.address_id} address={self.address} postal_code={self.postal_code}>'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class AddressSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Address
        include_fk = True
        load_instance = True
        transient = True
