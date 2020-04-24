from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class Rate(Model):
    __tablename__ = 'rates'

    rate_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    description = Column(db.Text, nullable=False)

    #many-to-one intervals per rate
    intervals = relationship('Interval', backref=db.backref('rate'))

    def __repr__(self):
        return f'<Rate rate_id={self.rate_id} description={self.description}>'
