

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

    #many-to-one channels per meter
    meter = db.relationship('Meter', backref=db.backref('channels'))

    def __repr__(self):
        return f'<Channel channel_id={self.channel_id} meter_id={self.meter_id} channel_type={self.channel_type}>'