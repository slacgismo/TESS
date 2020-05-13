from datetime import datetime
from sqlalchemy.types import TIMESTAMP

#TODO: add in user mixin for built in flask-user capabilities
# from flask_user import UserMixin

from web.models.address import Address
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class User(Model):

    __tablename__ = 'users'

    user_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(db.String(50), unique=True, nullable=False)
    first_name = Column(db.String(64), nullable=False)
    last_name = Column(db.String(64), nullable=False)
    address_id = Column(db.Integer, db.ForeignKey('addresses.address_id'))
    is_active = Column(db.Boolean(), nullable=False)
    is_archived = Column(db.Boolean(), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


    #relationships
    login = relationship('Login', backref=db.backref('user'), uselist=False)
    group = relationship('Group', backref=db.backref('user'), uselist=False)