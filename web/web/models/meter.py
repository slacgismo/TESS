import enum
from marshmallow import fields
from sqlalchemy.types import TIMESTAMP
from web.models.utility import Utility
from datetime import datetime, timedelta
from .service_location import ServiceLocationSchema
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from web.models.service_location import ServiceLocation
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class MeterType(enum.Enum):
    AXR_SD = 'AXR-SD'
    KWH_DEMAND = 'kWh/Demand' 
    TOD_KWH_DEMAND = 'Time-of-Day/KWH/Demand'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type name.'''
 
        for meter_type in MeterType:
            if meter_type.value == str_value:
                return meter_type.name
        
        return False


class Meter(Model):
    __tablename__ = 'meters'

    #composite primary key - meter_id, utility_id, and service_location_id
    meter_id = Column(db.String(64), primary_key=True, nullable=False)
    utility_id = Column(db.Integer, db.ForeignKey('utilities.utility_id'), primary_key=True, nullable=False)
    service_location_id = Column(db.String(64), db.ForeignKey('service_locations.service_location_id'), primary_key=True, nullable=False)
    
    feeder = Column(db.String(45), nullable=False) 
    substation = Column(db.String(45), nullable=False) 
    meter_type = Column(db.Enum(MeterType), nullable=False) 
    is_active = Column(db.Boolean(False), nullable=False)
    is_archived = Column(db.Boolean(False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    #many-to-one meters per service location
    service_location = relationship('ServiceLocation', backref=db.backref('meters'))
    
    #many-to-one meters per utility
    utility = relationship('Utility', backref=db.backref('meters'))

    def get_interval_count(self, start, end):
        '''Takes in start and end ISO8601 times, 
            returns the interval count (integer) between start / end times, inclusively'''
        
        self_intervals = self.intervals

        selected_intervals = []
        
        if start == None:
            start = datetime.now() - timedelta(days=1)

        if end == None:
            end = datetime.now()

        for interval in self_intervals:
            if interval.start_time >= start and interval.end_time <= end:
                selected_intervals.append(interval)

        return len(selected_intervals)

    def get_rates(self):
        '''Returns meter instance's rates as a set'''

        rates = set()

        for interval in self.intervals:
            rates.add(interval.rate.description)
        
        return rates
    
    def get_all_intervals(self):
        '''Returns all meter instances's intervals in a list'''
        
        intervals_list = []

        for interval in self.intervals:
            intervals_list.append(interval.interval_id)
        
        return intervals_list

    def __repr__(self):
        return f'<Meter meter_id={self.meter_id} is_active={self.is_active}>'


class MeterSchema(SQLAlchemyAutoSchema):
    meter_type = fields.Method("get_meter_type")
    service_location = fields.Nested(ServiceLocationSchema)

    def get_meter_type(self, obj):
        return obj.meter_type.value

    class Meta:
        model = Meter
        include_relationships = True
        load_instance = True
        include_fk = True
