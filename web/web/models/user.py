from datetime import datetime
from sqlalchemy.types import TIMESTAMP

from flask_user import UserMixin
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

    id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)

    #user email information
    email = Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = Column(TIMESTAMP)

    #user information
    first_name = Column(db.String(64), nullable=False)
    last_name = Column(db.String(64), nullable=False)
    address_id = Column(db.Integer, db.ForeignKey('addresses.address_id'))
    utility_id = Column(db.Integer, db.ForeignKey('utilities.utility_id'), nullable=False)

    is_active = Column(db.Boolean(), nullable=False)
    is_archived = Column(db.Boolean(), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    utility = relationship('Utility', backref=db.backref('groups'))

    def get_roles(self):
        '''returns list of user role object'''
        roles = []
        for group in self.groups:
            roles.append(group.role)
        return roles

class UserSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_fk = True
        load_instance = True
        ordered = True