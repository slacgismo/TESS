


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

    def __repr__(self):
        return f'<Address address_id={self.address_id} address={self.address} postal_code={self.postal_code}>'