import enum
from web.models.rate import Rate
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import ForeignKeyConstraint
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class Status(enum.Enum):
   VALID = 'valid'
   INVALID = 'invalid'

   @staticmethod
   def check_value(str_value):
       '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type name.'''
       for status_type in Status:
           if status_type.value == str_value:
               return status_type
       return False

class MeterInterval(Model):
    __tablename__ = 'meter_intervals'
    
    meter_interval_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = Column(db.Integer, db.ForeignKey('meters.meter_id'), nullable=False)
    rate_id = Column(db.Integer, db.ForeignKey('rates.rate_id'), nullable=False) 
    status = Column(db.Enum(Status), nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    e = Column(db.Float, nullable=False)
    qtmp = Column(db.Float, nullable=False)
    p_bid = Column(db.Float, default=0, nullable=False)
    q_bid = Column(db.Float, default=0, nullable=False)
    mode = Column(db.Boolean(create_constraint=True), default=0, nullable=False)
    
    # many-to-one meter intervals per rate
    rate = relationship('Rate', backref=db.backref('meter_intervals'))

    @staticmethod
    def get_interval_coverage(interval_id_list):
        '''Takes in list of meter interval ids, 
            returns list of tuples for start and end times in ISO8601 format'''

        selected_intervals = MeterInterval.query.filter(MeterInterval.meter_interval_id.in_(interval_id_list)).all()
        start_end_tuples_list = []

        for meter_interval in selected_intervals:
            start_end_tuples_list.append((meter_interval.start_time, meter_interval.end_time))

        return start_end_tuples_list

    def __repr__(self):
        return f'<MeterInterval meter_interval_id={self.meter_interval_id} meter_id={self.meter_id} end_time={self.end_time} e={self.e}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################

class MeterIntervalSchema(SQLAlchemyAutoSchema):
    status = fields.Method('get_status', deserialize='load_status')

    
    def get_status(self, obj):
        return obj.status.value

    def load_status(self, value):
        status_enum = Status.check_value(value)
        if not status_enum:
            raise ValidationError(f'{value} is an invalid status input')
        return status_enum

    class Meta:
        model = MeterInterval
        load_instance = True
        include_fk = True