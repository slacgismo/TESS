from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import enum
from sqlalchemy import and_, ForeignKeyConstraint
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
import os

#variables for connecting to db
dbuser = os.environ.get('dbuser', '')
dbpass = os.environ.get('dbpass', '')

#Instatiate a SQLAlchemy object
db = SQLAlchemy()

#enum fields for meter_type column in meter
class MeterType(enum.Enum):

    #What names for the meter types? 
    #Replace one, two, three with corresponding names
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

    #many-to-one meters per service location
    service_location = db.relationship('ServiceLocation', backref=db.backref('meters'))
    
    #many-to-one meters per utility
    utility = db.relationship('Utility', backref=db.backref('meters'))

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


#local connection - switch to rds to deploy
def connect_to_db(app, db_uri = 'mysql+pymysql://{0}:{1}@localhost/meter_tel'.format(dbuser, dbpass)):
    '''Connect the database to app'''

    app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ECHO'] = True

    db.app = app
    db.init_app(app)


# if __name__ == '__main__':
    
#     from api.v1.api import app
#     connect_to_db(app)

#     #for using interactively
#     print('Connected to DB.')