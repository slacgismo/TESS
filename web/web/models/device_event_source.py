from sqlalchemy import text, func
from sqlalchemy.types import TIMESTAMP
from web.database import (db, Model, Column)
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema


class EventingDevice(Model):
    __tablename__ = 'eventing_devices'
    ed_id = Column(db.Integer,
                   primary_key=True,
                   autoincrement=True,
                   nullable=False)
    device_id = Column(db.String(64), unique=True)


class EventingDeviceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = EventingDevice
        load_instance = True


class DeviceEventSource(Model):
    __tablename__ = 'device_events'
    des_id = Column(db.Integer,
                    primary_key=True,
                    autoincrement=True,
                    nullable=False)
    event_data = Column(db.JSON)
    created_at = Column(TIMESTAMP, server_default=func.now())
    ed_id = Column(db.Integer,
                   db.ForeignKey(EventingDevice.ed_id),
                   unique=False,
                   nullable=False)


class DeviceEventSourceSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = DeviceEventSource
        load_instance = True
