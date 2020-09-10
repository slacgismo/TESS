from sqlalchemy import text, func
from sqlalchemy.types import TIMESTAMP
from web.database import (db, Model, Column)
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class DeviceEventSource(Model):
    __tablename__ = 'device_events'
    des_id = Column(db.Integer,
                    primary_key=True,
                    autoincrement=True,
                    nullable=False)
    event_data = Column(db.JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())


class DeviceEventSourceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DeviceEventSource
        load_instance = True
