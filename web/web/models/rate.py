

class Rate(db.Model):

    __tablename__ = 'rates'

    rate_id = db.Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    description = db.Column(db.Text, nullable=False)

    #many-to-one intervals per rate
    intervals = db.relationship('Interval', backref=db.backref('rate'))

    def __repr__(self):
        return f'<Rate rate_id={self.rate_id} description={self.description}>'
