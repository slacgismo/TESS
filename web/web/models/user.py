from datetime import datetime
from sqlalchemy.types import TIMESTAMP

from flask_user import UserMixin
from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from web.models.address import Address
from web.models.role import Role, RoleType
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
    address = relationship('Address', backref=db.backref('addresses'))

    def get_roles(self):
        '''returns list of user role object'''
        roles = []
        for group in self.groups:
            roles.append(group.role)
        return roles

class UserSchema(SQLAlchemyAutoSchema):
    roles = fields.Method('get_roles', dump_only=True) #deserialize='load_role_type'
    address = fields.Method('get_address', dump_only=True)
    utility = fields.Method('get_utility_name', dump_only=True)

    def get_roles(self, obj):
        roles = obj.get_roles()
        result_roles = []
        for role in roles:
            result_roles.append(role.name.value)
        return result_roles

    def get_address(self, obj):
        address = {'city': obj.address.city,
                   'country': obj.address.country,
                   'postal code': obj.address.postal_code}
        return address

    def get_utility_name(self, obj):
        return obj.utility.name

    # def load_role_type(self, value):
    #     role_enum = RoleType.check_value(value)
    #     if not role_enum:
    #         raise ValidationError(f'{value} is an invalid role type')
    #     return role_enum

    class Meta:
        model = User
        include_fk = True
        load_instance = True
        ordered = True