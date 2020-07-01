from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text, func
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

    address = Column(db.String(100), nullable=False)

    address2 = Column(db.String(64))

    district = Column(db.String(64))

    city = Column(db.String(100), nullable=False)

    country = Column(db.String(100), nullable=False)

    postal_code = Column(db.String(64), nullable=False)

    phone = Column(db.String(64))

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    # Methods
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
