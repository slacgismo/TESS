from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.rate import Rate
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class MeterInterval(Model):
    __tablename__ = 'meter_intervals'

    meter_interval_id = Column(db.Integer,
                               autoincrement=True,
                               primary_key=True,
                               nullable=False)

    meter_id = Column(db.Integer,
                      db.ForeignKey('meters.meter_id'),
                      nullable=False)

    rate_id = Column(db.Integer,
                     db.ForeignKey('rates.rate_id'),
                     nullable=False)

    start_time = Column(TIMESTAMP, nullable=False)

    end_time = Column(TIMESTAMP, nullable=False)

    e = Column(db.Float, nullable=False)

    qmtp = Column(db.Float, nullable=False)

    p_bid = Column(db.Float, default=0, nullable=False)

    q_bid = Column(db.Float, default=0, nullable=False)

    mode_market = Column(db.Float, default=0, nullable=False)

    mode_dispatch = Column(db.Float, default=0, nullable=False)

    is_bid = Column(db.Boolean(), default=False, nullable=False)

    @staticmethod
    def get_interval_coverage(interval_id_list):
        '''Takes in list of meter interval ids,
            returns list of tuples for start and end times in ISO8601 format'''

        selected_intervals = MeterInterval.query.filter(
            MeterInterval.meter_interval_id.in_(interval_id_list)).all()
        start_end_tuples_list = []

        for meter_interval in selected_intervals:
            start_end_tuples_list.append(
                (meter_interval.start_time, meter_interval.end_time))

        return start_end_tuples_list

    # Methods
    def __repr__(self):
        return f'<MeterInterval meter_interval_id={self.meter_interval_id} meter_id={self.meter_id} end_time={self.end_time} e={self.e}>'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class MeterIntervalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MeterInterval
        load_instance = True
        include_fk = True

# marshmallow errors out if RateSchema is declared on models/rate.py
# requires meter_interval to be initialized before RateSchema is declared

class RateSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Rate
        load_instance = True
        include_fk = True
