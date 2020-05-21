from datetime import datetime
from sqlalchemy.types import TIMESTAMP

from flask_login import UserMixin
from marshmallow import post_load, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from web.models.address import Address
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class User(UserMixin, Model):

    __tablename__ = 'users'

    user_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)

    #user email information
    email = Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = Column(TIMESTAMP, nullable=False)

    #user information
    first_name = Column(db.String(64), nullable=False)
    last_name = Column(db.String(64), nullable=False)
    address_id = Column(db.Integer, db.ForeignKey('addresses.address_id'))

    is_active = Column(db.Boolean(), nullable=False)
    is_archived = Column(db.Boolean(), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

#def generate_confirmation_token(self, expiration=3600):

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        ordered = True
        exlude = ('emailed_confirmed_at',)

    def get_email_confirmed_at(self, obj):
        return obj.get_email_confirmed_at
    
    # @post_load
    # def make_user(self, data, **kwargs):
    #     return User(**data)
