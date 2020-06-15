from datetime import datetime
from flask_user import UserMixin
from sqlalchemy.types import TIMESTAMP
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.address import Address, AddressSchema
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

    id = Column(db.Integer,
                primary_key=True,
                autoincrement=True,
                nullable=False)

    # User email information
    email = Column(db.String(255), nullable=False, unique=True)
    email_confirmed_at = Column(TIMESTAMP)

    # User information
    first_name = Column(db.String(64), nullable=False)
    last_name = Column(db.String(64), nullable=False)
    address_id = Column(db.Integer, db.ForeignKey('addresses.address_id'))
    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),
                        nullable=False)

    is_active = Column(db.Boolean(), nullable=False)
    is_archived = Column(db.Boolean(), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Relationships
    utility = relationship('Utility', backref=db.backref('users'))
    address = relationship('Address', backref=db.backref('users'), uselist=False)

    # Methods
    def get_roles(self):
        '''Returns list of user role objects'''

        roles = []
        for group in self.groups:
            roles.append(group.role)
        return roles

    def does_user_role_exist(self, role_name):
        '''Returns true or false whether user has assigned role'''

        for group in self.groups:
            if group.role.name.value == role_name:
                return True
        return False


##########################
### MARSHMALLOW SCHEMA ###
##########################


class UserSchema(SQLAlchemyAutoSchema):
    roles = fields.Method('get_roles', dump_only=True)
    postal_code = fields.Method('get_postal_code', dump_only=True)
    address = fields.Nested(AddressSchema(), load_only=True)

    def get_roles(self, obj):
        roles = obj.get_roles()
        result_roles = []
        for role in roles:
            result_roles.append(role.name.value)
        return result_roles

    def get_postal_code(self, obj):
        address = {
            'postal code': obj.address.postal_code,
            'country': obj.address.country
        }
        return address

    class Meta:
        model = User
        include_fk = True
        load_instance = True
        transient = True
