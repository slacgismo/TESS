from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
from sqlalchemy import and_


#Instatiate a SQLAlchemy object
db = SQLAlchemy()


class Rate(db.Model):

    __tablename__ = 'rates'

    rate_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

    #many-to-one meters per rate
    meters = db.relationship('Meter', backref=db.backref('rate'))

    def __repr__(self):
        return f'<Rate rate_id={self.rate_id} description={self.description}>'


class Country(db.Model):

    __tablename__ = 'countries'

    country_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    last_update = db.Column(db.Timestamp, nullable=False)

    #many-to-one cities per country
    cities = db.relationship('City', backref=db.backref('country'))

    def __repr__(self):
        return f'<Country country_id={self.country_id} name={self.name}>'


class City(db.Model):

    __tablename__ = 'cities'

    city_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    country_id = db.Column(db.Integer, db.ForeignKey('countries.country_id'))
    last_update = db.Column(db.Timestamp, nullable=False)

    #many-to-one addresses per city
    addresses = db.relationship('Address', backref=db.backref('city'))

    def __repr__(self):
        return f'<City city_id={self.city_id} name={self.name}>'


class Address(db.Model):

    __tablename__ = 'addresses'

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    address = db.Column(db.String(100), nullable=False)
    address2 = db.Column(db.String(64))
    district = db.Coumn(db.String(64))
    city_id = db.Column(db.Integer, db.ForeignKey('cities.city_id'))
    postal_code = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(64))
    last_update = db.Column(db.Timestamp, nullable=False)
    location = db.Column(db.Geometry)

    #one-to-one service location per address
    service_location = db.relationship('ServiceLocation', backref=db.backref('address'), uselist=False)

    def __repr__(self):
        return f'<Address address_id={self.address_id} address={self.address} postal_code={self.postal_code}>'


class ServiceLocation(db.Model):

    __tablename__ = 'service_locations'

    service_location_id = db.Column(db.String(64), primary_key=True, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    map_location = db.Column(db.String(64), nullable=False)

    #many-to-one meters per service location
    meters = db.relationship('Meter', backref=db.backref('meter'))

    def __repr__(self):
        return f'<ServiceLocation service_location_id={self.service_location_id} address_id={self.address_id}>'


class Utility(db.Model):
    
    __tablename__ = 'utilities'

    utility_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    name = db.Column(db.String(64), nullable=False)
    subscription_start = db.Column(db.Timestamp, nullable=False)
    subscription_end = db.Column(db.Timestamp, nullable=False)

    #many-to-one meters per utility
    meters = db.relationship('Meter', backref=db.backref('utility'))

    def __repr__(self):
        return f'<Utility utility_id={self.utility_id} name={self.name}>'


#association table for meters-channels many-to-many relationship
meter_channels = db.Table('meter_channels',
            db.Column('meter_id', db.String(64), db.ForeignKey('meters.meter_id')),
            db.Column('channel_id', db.Integer, db.ForeignKey('channels.channel_id'))
)


class Meter(db.Model):
    
    __tablename__ = 'meters'

    meter_id = db.Column(db.String(64), primary_key=True, nullable=False)
    utility_id = db.Column(db.Integer, db.ForeignKey('utilities.utility_id'), nullable=False)
    service_location_id = db.Column(db.String(64), db.ForeignKey('service_locations.service_location_id'), nullable=False)
    rate_id = db.Column(db.Integer, db.ForeignKey('rates.rate_id'), nullable=False)
    feeder = db.Column(db.String(45), nullable=False)
    substation = db.Column(db.String(45), nullable=False)
    meter_type = db.Column(db.String(65), nullable=False)
    is_active = db.Column(db.Boolean(False))
    is_archived = db.Column(db.Boolean(False))

    #many-to-many meters per channels
    channels = db.relationship('Channel', secondary=meter_channels, backref=db.backref('meters'))

    #many-to-one intervals per meter
    intervals = db.relationship('Interval', backref=db.backref('meter'))


    def __repr__(self):

        return f'<Meter meter_id={self.meter_id} is_active={self.is_active}>'


class Channel(db.Model):

    __tablename__ = 'channels'

    channel_id = db.Column(db.Integer, primary_key=True, nullable=False)
    channel_type = db.Column(db.String(64), nullable=False)

    def __repr__(self):

        return f'<Channel channel_id={self.channel_id} channel_type={self.channel_type}>'


class Interval(db.Model):

    __tablename__ = 'intervals'
    
    interval_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = db.Column(db.String(64), db.ForeignKey('meters.meter_id'), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    start_time = db.Column(db.Timestamp, nullable=False)
    end_time = db.Column(db.Timestamp, nullable=False)
    value = db.Column(db.Float, nullable=False)

    @staticmethod
    def get_interval_count(start, end):
        '''Takes in start and end ISO8601 times, returns the interval count (integer) between start / end times, inclusively'''
        
        intervals = Interval.query.filter(and_(Interval.start_time == start, Interval.end_time == end)).all()

        return len(intervals)
    
    @staticmethod
    def get_interval_coverage(interval_id_list):
        '''Takes in list of interval ids, returns list of tuples for start and end times in ISO8601 format'''

        start_end_tuple_list = []

        intervals = Interval.query.filter(Interval.interval_id.in_(interval_id_list)).all()

        for row in intervals:
            start_end_tuple_list.append((row.start_time, row.end_time))

        return start_end_tuple_list

    def __repr__(self):

        return f'<Interval interval_id={self.interval_id} end_time={self.end_time} value={self.value}>'

#connect to RDS database