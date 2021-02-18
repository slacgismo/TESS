import enum
from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text, func
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError

from web.models.channel import Channel, ChannelSchema
from web.models.meter_interval import MeterInterval
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class MeterType(enum.Enum):
    RESIDENTIAL = 'Residential'
    COMMERCIAL = 'Commercial'
    PRODUCTION = 'Production'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type name.'''

        for meter_type in MeterType:
            if meter_type.value == str_value:
                return meter_type

        return False


class Meter(Model):
    __tablename__ = 'meters'

    # Composite primary key: meter_id, utility_id, and service_location_id
    meter_id = Column(db.Integer,
                      primary_key=True,
                      autoincrement=True,
                      nullable=False)
    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),
                        primary_key=True,
                        nullable=False)
    service_location_id = Column(
        db.Integer,
        db.ForeignKey('service_locations.service_location_id'),
        primary_key=True,
        nullable=False)
    home_hub_id = Column(db.Integer,
                         db.ForeignKey('home_hubs.home_hub_id'),
                         nullable=False)
    transformer_id = Column(db.Integer,
                            db.ForeignKey('transformers.transformer_id'),
                            nullable=True)
    alternate_meter_id = Column(db.String(64), unique=True)
    feeder = Column(db.String(45), nullable=False)
    substation = Column(db.String(45), nullable=False)
    meter_type = Column(db.Enum(MeterType), nullable=False)
    is_active = Column(db.Boolean(), default=False, nullable=False)
    is_archived = Column(db.Boolean(), default=False, nullable=False)

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Methods
    def get_interval_count(self, start, end):
        '''Takes in start and end ISO8601 times,
            returns the interval count (integer) between start / end times, inclusively'''

        self_intervals = self.meter_intervals
        selected_intervals = []

        if start == None:
            start = datetime.now() - timedelta(days=1)

        if end == None:
            end = datetime.now()

        for meter_interval in self_intervals:
            if meter_interval.start_time >= start and meter_interval.end_time <= end:
                selected_intervals.append(meter_interval)

        return len(selected_intervals)

    def get_rates(self):
        '''Returns meter instance's rates as a list'''

        rates = []
        for meter_interval in self.meter_intervals:
            if meter_interval.rate.description not in rates:
                rates.append(meter_interval.rate.description)

        return rates

    def get_channels(self):
        '''Returns meter instance's channel settings as a list'''

        channels = Meter.query.\
                        join(Meter.channels). \
                        all()
        return channels

    def get_all_intervals(self):
        '''Returns all meter instances's intervals in a list'''

        intervals_list = []
        for meter_interval in self.meter_intervals:
            intervals_list.append(meter_interval.meter_interval_id)

        return intervals_list

    def __repr__(self):
        return f'<Meter meter_id={self.meter_id} is_active={self.is_active}>'

    # Relationships
    channels = relationship('Channel', backref=db.backref('meter'))

    meter_intervals = relationship('MeterInterval',
                                   backref=db.backref('meter'))


##########################
### MARSHMALLOW SCHEMA ###
##########################


class MeterSchema(SQLAlchemyAutoSchema):
    meter_type = fields.Method('get_meter_type', deserialize='load_meter_type')
    map_location = fields.Method('get_map_location',
                                 deserialize='load_map_location')
    postal_code = fields.Method('get_postal_code')
    rates = fields.Method('get_rates', dump_only=True)
    channels = fields.Nested(ChannelSchema(many=True), dump_only=True)
    interval_count = fields.Method('get_interval_count', dump_only=True)
    interval_coverage = fields.Method('get_interval_coverage', dump_only=True)
    user_id = fields.Method('get_user_id', dump_only=True)

    # Marshmallow methods
    def get_postal_code(self, obj):
        return obj.service_location.address.postal_code

    def get_map_location(self, obj):
        return obj.service_location.map_location

    def load_map_location(self, value):
        return

    def get_meter_type(self, obj):
        return obj.meter_type.value

    def load_meter_type(self, value):
        meter_enum = MeterType.check_value(value)
        if not meter_enum:
            raise ValidationError(f'{value} is an invalid meter type')
        return meter_enum

    def get_rates(self, obj):
        return obj.get_rates()

    def get_interval_count(self, obj):
        start = self.context['start'] if 'start' in self.context else None
        end = self.context['end'] if 'end' in self.context else None
        return obj.get_interval_count(start, end)

    def get_interval_coverage(self, obj):
        coverage = self.context[
            'coverage'] if 'coverage' in self.context else []
        return MeterInterval.get_interval_coverage(coverage)

    def get_user_id(self, obj):
        users = obj.service_location.address.users
        if users:
            user_ids = [ user.id for user in users ]
            return user_ids
        return []

    class Meta:
        model = Meter
        load_instance = True
        include_fk = True
