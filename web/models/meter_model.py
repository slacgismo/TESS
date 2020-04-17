from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import enum
from sqlalchemy import and_, ForeignKeyConstraint
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
import os

#variables for connecting to db
dbuser = os.environ['dbuser']
dbpass = os.environ['dbpass']

#Instatiate a SQLAlchemy object
db = SQLAlchemy()


class Rate(db.Model):

    __tablename__ = 'rates'

    rate_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

    #many-to-one intervals per rate
    intervals = db.relationship('Interval', backref=db.backref('rate'))

    def __repr__(self):
        return f'<Rate rate_id={self.rate_id} description={self.description}>'


class Address(db.Model):

    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    address2 = db.Column(db.String(64))
    district = db.Column(db.String(64))
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
    postal_code = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(64))
    last_update = db.Column(TIMESTAMP, nullable=False)

    #one-to-one service location per address
    service_location = db.relationship('ServiceLocation', backref=db.backref('address'), uselist=False)

    def __repr__(self):
        return f'<Address address_id={self.address_id} address={self.address} postal_code={self.postal_code}>'


class ServiceLocation(db.Model):

    __tablename__ = 'service_locations'

    service_location_id = db.Column(db.String(64), primary_key=True, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=False)
    map_location = db.Column(db.String(64), nullable=False)

    #many-to-one meters per service location
    meters = db.relationship('Meter', backref=db.backref('meter'))

    def __repr__(self):
        return f'<ServiceLocation service_location_id={self.service_location_id} address_id={self.address_id}>'


class Utility(db.Model):
    
    __tablename__ = 'utilities'

    utility_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    subscription_start = db.Column(TIMESTAMP, nullable=False)
    subscription_end = db.Column(TIMESTAMP, nullable=False)

    #many-to-one meters per utility
    meters = db.relationship('Meter', backref=db.backref('utility'))

    def __repr__(self):
        return f'<Utility utility_id={self.utility_id} name={self.name}>'

#enum fields for meter_type column in meter
class MeterType(enum.Enum):

    #what values for meter type?
    one = "kWh/Demand" 
    two = "Time-of-Day/KWH/Demand"
    three = "AXR-SD"

class Meter(db.Model):
    
    __tablename__ = 'meters'

    #composite primary key - meter_id, utility_id, and service_location_id
    meter_id = db.Column(db.String(64), primary_key=True, nullable=False)
    utility_id = db.Column(db.Integer, db.ForeignKey('utilities.utility_id'), primary_key=True, nullable=False)
    service_location_id = db.Column(db.String(64), db.ForeignKey('service_locations.service_location_id'), primary_key=True, nullable=False)
    
    feeder = db.Column(db.String(45), nullable=False) 
    substation = db.Column(db.String(45), nullable=False) #?representation of transformer (kWh)
    meter_type = db.Column(db.Enum(MeterType), nullable=False) 
    is_active = db.Column(db.Boolean(False))
    is_archived = db.Column(db.Boolean(False))

    #many-to-one intervals per meter
    intervals = db.relationship('Interval', backref=db.backref('meter'))

    #many-to-one channels per meter
    channels = db.relationship('Channel', backref=db.backref('meter'))

    def get_interval_count(self, start, end):
        '''Takes in start and end ISO8601 times, 
            returns the interval count (integer) between start / end times, inclusively'''

        self_intervals = self.intervals
        selected_intervals = self_intervals.filter(and_(self_intervals.start_time >= start, self_intervals.end_time <= end)).all()

        return len(selected_intervals)

    def __repr__(self):

        return f'<Meter meter_id={self.meter_id} is_active={self.is_active}>'


class Channel(db.Model):

    __tablename__ = 'channels'

    channel_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = db.Column(db.String(64), nullable=False)
    utility_id = db.Column(db.Integer, nullable=False)
    service_location_id = db.Column(db.String(64), nullable=False)
    setting = db.Column(db.Integer, nullable = False) 
    channel_type = db.Column(db.String(64), nullable=False)

    #composite foreign key to meter
    __table_args__ = (ForeignKeyConstraint([meter_id, utility_id, service_location_id],
                                           [Meter.meter_id, Meter.utility_id, Meter.service_location_id]), 
                                           {})

    def __repr__(self):

        return f'<Channel channel_id={self.channel_id} meter_id={self.meter_id} channel_type={self.channel_type}>'

#enum fields for status column in interval
class Status(enum.Enum):

    #what values?
    one = "valid"

class Interval(db.Model):

    __tablename__ = 'intervals'
    
    interval_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = db.Column(db.String(64), nullable=False)
    utility_id = db.Column(db.Integer, nullable=False)
    service_location_id = db.Column(db.String(64), nullable=False)
    rate_id = db.Column(db.Integer, db.ForeignKey('rates.rate_id'), nullable=False) 
    status = db.Column(db.Enum(Status), nullable=False)
    start_time = db.Column(TIMESTAMP, nullable=False)
    end_time = db.Column(TIMESTAMP, nullable=False)
    value = db.Column(db.Float, nullable=False)

    #composite foreign key to meter
    __table_args__ = (ForeignKeyConstraint([meter_id, utility_id, service_location_id],
                                           [Meter.meter_id, Meter.utility_id, Meter.service_location_id]), 
                                           {})

    @staticmethod
    def get_interval_coverage(interval_id_list):
        '''Takes in list of interval ids, 
            returns list of tuples for start and end times in ISO8601 format'''
        
        #improve for error handling (id doesn't exist)

        selected_intervals = Interval.query.filter(Interval.interval_id.in_(interval_id_list)).all()
        start_end_tuples_list = []

        for interval in selected_intervals:
            start_end_tuples_list.append((interval.start_time, interval.end_time))

        return start_end_tuples_list

    def __repr__(self):

        return f'<Interval interval_id={self.interval_id} meter_id={self.meter_id} end_time={self.end_time} value={self.value}>'

#local connection - switch to rds to deploy
def connect_to_db(app, db_uri = 'mysql+pymysql://{0}:{1}@localhost/meter_tel'.format(dbuser, dbpass)):
    '''Connect the database to app'''

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    db.app = app
    db.init_app(app)


if __name__ == '__main__':
    
    from api.v1.api import *
    connect_to_db(app)

    #for using interactively
    print('Connected to DB.')