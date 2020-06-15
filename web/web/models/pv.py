from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields

from web.models.meter import Meter, MeterSchema
from web.models.home_hub import HomeHub
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Pv(Model):
    __tablename__ = 'pvs'

    pv_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    home_hub_id = Column(db.Integer, db.ForeignKey('home_hubs.home_hub_id'), nullable=False)
    meter_id = Column(db.Integer, db.ForeignKey('meters.meter_id'), nullable=False)
    q_rated = Column(db.Float, nullable=False)
    is_active = Column(db.Boolean(False), nullable=False)
    is_archived = Column(db.Boolean(False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    home_hub = relationship('HomeHub', backref=db.backref('pvs'))
    meter = relationship('Meter', backref=db.backref('meters'))

    def __repr__(self):
        return f'<Pv pv_id={self.pv_id} home_hub_id={self.home_hub_id} created_at={self.created_at}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################

class PvSchema(SQLAlchemyAutoSchema):
    meter = fields.Nested(MeterSchema(), dump_only=True)

    class Meta:
        model = Pv
        load_instance = True
        include_fk = True
