from sqlalchemy.types import TIMESTAMP
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

    address_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    address = Column(db.String(100), nullable=False)
    address2 = Column(db.String(64))
    district = Column(db.String(64))
    city = Column(db.String(100), nullable=False)
    country = Column(db.String(100), nullable=False)
    postal_code = Column(db.String(64), nullable=False)
    phone = Column(db.String(64))
    last_update = Column(TIMESTAMP, nullable=False)

    def __repr__(self):
        return f'<Address address_id={self.address_id} address={self.address} postal_code={self.postal_code}>'