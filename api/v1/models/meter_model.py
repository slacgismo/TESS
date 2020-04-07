from flask import Flask
from flask_sqlalchemy import SQLAlchemy 
import enum
from sqlalchemy import and_, ForeignKeyConstraint


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
    district = db.Coumn(db.String(64))
    city = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(100), nullable=False)
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


class MeterType(enum.Enum):

    #enum table for meter type - what values for meter type?
    one = "kWh/Demand" #example


class Meter(db.Model):
    
    __tablename__ = 'meters'

    #composite key - meter_id, utility_id and service_location_id
    meter_id = db.Column(db.String(64), primary_key=True, nullable=False)
    utility_id = db.Column(db.Integer, db.ForeignKey('utilities.utility_id'), primary_key=True, nullable=False)
    service_location_id = db.Column(db.String(64), db.ForeignKey('service_locations.service_location_id'), primary_key=True, nullable=False)
    
    feeder = db.Column(db.String(45), nullable=False) 
    substation = db.Column(db.String(45), nullable=False) #?representation of transformer (kWh)
    meter_type = db.Column(enum.Enum(MeterType), nullable=False) #can meter type change for a particular meter?
    is_active = db.Column(db.Boolean(False))
    is_archived = db.Column(db.Boolean(False))

    #many-to-one intervals per meter
    intervals = db.relationship('Interval', backref=db.backref('meter'))

    #many-to-one channels per meter
    channels = db.relationship('Channel', backref=db.backref('meter'))

    def __repr__(self):

        return f'<Meter meter_id={self.meter_id} is_active={self.is_active}>'


class Channel(db.Model):

    __tablename__ = 'channels'

    channel_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = db.Column(db.String(64), nullable=False)
    setting = db.Column(db.Integer, nullable = False) #enum field?
    channel_type = db.Column(db.String(64), nullable=False)
    __table_args__ = (ForeignKeyConstraint([meter_id], [Meter.meter_id]), {})
    # need utility id and service location id?

    def __repr__(self):

        return f'<Channel channel_id={self.channel_id} meter_id={self.meter_id} channel_type={self.channel_type}>'


class Interval(db.Model):

    __tablename__ = 'intervals'
    
    interval_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = db.Column(db.String(64), db.ForeignKey('meters.meter_id'), nullable=False)
    rate_id = db.Column(db.Integer, db.ForeignKey('rates.rate_id'), nullable=False) 
    status = db.Column(db.String(64), nullable=False)
    start_time = db.Column(db.Timestamp, nullable=False)
    end_time = db.Column(db.Timestamp, nullable=False)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):

        return f'<Interval interval_id={self.interval_id} meter_id={self.meter_id} end_time={self.end_time} value={self.value}>'

####### CONNECT TO RDS #######
