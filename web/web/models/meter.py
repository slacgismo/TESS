import enum
from web.models.utility import Utility
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class MeterType(enum.Enum):
    one = "kWh/Demand" 
    two = "Time-of-Day/KWH/Demand"
    three = "AXR-SD"


class Meter(Model):
    __tablename__ = 'meters'

    #composite primary key - meter_id, utility_id, and service_location_id
    meter_id = Column(db.String(64), primary_key=True, nullable=False)
    utility_id = Column(db.Integer, db.ForeignKey('utilities.utility_id'), primary_key=True, nullable=False)
    service_location_id = Column(db.String(64), db.ForeignKey('service_locations.service_location_id'), primary_key=True, nullable=False)
    
    feeder = Column(db.String(45), nullable=False) 
    substation = Column(db.String(45), nullable=False) #?representation of transformer (kWh)
    meter_type = Column(db.Enum(MeterType), nullable=False) 
    is_active = Column(db.Boolean(False))
    is_archived = Column(db.Boolean(False))

    #many-to-one meters per service location
    service_location = relationship('ServiceLocation', backref=db.backref('meters'))
    
    #many-to-one meters per utility
    utility = relationship('Utility', backref=db.backref('meters'))

    #interval count
    def get_interval_count(self, start, end):
        '''Takes in start and end ISO8601 times, 
            returns the interval count (integer) between start / end times, inclusively'''
        
        #get the meter's intervals
        self_intervals = self.intervals

        selected_intervals = []
        
        for interval in self_intervals:
            if interval.start_time >= start and interval.end_time <= end:
                selected_intervals.append(interval)

        return len(selected_intervals)

    def __repr__(self):
        return f'<Meter meter_id={self.meter_id} is_active={self.is_active}>'