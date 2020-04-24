

class Status(enum.Enum):
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

    #many-to-one intervals per meter
    meter = db.relationship('Meter', backref=db.backref('intervals'))
    
    #many-to-one intervals per rate
    rate = db.relationship('Rate', backref=db.backref('intervals'))

    @staticmethod
    def get_interval_coverage(interval_id_list):
        '''Takes in list of interval ids, 
            returns list of tuples for start and end times in ISO8601 format'''
        
        #improve for error handling (id doesn't exist in list)

        selected_intervals = Interval.query.filter(Interval.interval_id.in_(interval_id_list)).all()
        start_end_tuples_list = []

        for interval in selected_intervals:
            start_end_tuples_list.append((interval.start_time, interval.end_time))

        return start_end_tuples_list

    def __repr__(self):
        return f'<Interval interval_id={self.interval_id} meter_id={self.meter_id} end_time={self.end_time} value={self.value}>'
