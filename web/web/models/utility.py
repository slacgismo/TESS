from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.types import TIMESTAMP

from web.models.meter import Meter
from web.models.user import User
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Utility(Model):
    __tablename__ = 'utilities'

    utility_id = Column(db.Integer,
                        primary_key=True,
                        autoincrement=True,
                        nullable=False)

    name = Column(db.String(64), nullable=False)

    subscription_start = Column(TIMESTAMP, nullable=False)

    subscription_end = Column(TIMESTAMP, nullable=False)

    # Methods
    def __repr__(self):
        return f'<Utility utility_id={self.utility_id} name={self.name}>'

    # Relationships
    meters = relationship('Meter', backref=db.backref('utility'))

    users = relationship('User', backref=db.backref('utility'))


##########################
### MARSHMALLOW SCHEMA ###
##########################


class UtilitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Utility
        include_fk = True
        load_instance = True
