


class ServiceLocation(db.Model):

    __tablename__ = 'service_locations'

    service_location_id = db.Column(db.String(64), primary_key=True, nullable=False)
    address_id = db.Column(db.Integer, db.ForeignKey('addresses.address_id'), nullable=False)
    map_location = db.Column(db.String(64), nullable=False)

    #one-to-one service location per address
    address = db.relationship('Address', backref=db.backref('service_locations'), uselist=False)

    def __repr__(self):
        return f'<ServiceLocation service_location_id={self.service_location_id} address_id={self.address_id}>'