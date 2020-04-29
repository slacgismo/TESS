from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from web.models.address import Address
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

    service_location_id = Column(db.String(64), primary_key=True, nullable=False)
    address_id = Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=False)
    map_location = Column(db.String(64), nullable=False)
    # created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    # updated_at = Column(TIMESTAMP, nullable=False,default=datetime.utcnow, onupdate=datetime.utcnow)

    #one-to-one service location per address
    address = relationship('Address', backref=db.backref('service_locations'), uselist=False)

    def __repr__(self):
        return f'<ServiceLocation service_location_id={self.service_location_id} address_id={self.address_id}>'