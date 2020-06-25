from datetime import datetime
from flask_user import UserMixin
from sqlalchemy.types import TIMESTAMP
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.alert import Alert
from web.models.user_notification import UserNotification
from web.models.address import Address, AddressSchema
from web.models.login import Login
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
    email = Column(db.String(255),
                   unique=True,
                   nullable=False)

    email_confirmed_at = Column(TIMESTAMP)

    # User information
    first_name = Column(db.String(64),
                        nullable=False)

    last_name = Column(db.String(64),
                       nullable=False)

    address_id = Column(db.Integer,
                        db.ForeignKey('addresses.address_id'),
                        unique=True,
                        nullable=False)

    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),
                        nullable=False)

    is_active = Column(db.Boolean(),
                       default=False,
                       nullable=False)

    is_archived = Column(db.Boolean(), 
                         default=False, 
                         nullable=False)

    created_at = Column(TIMESTAMP,
                        default=datetime.utcnow,
                        nullable=False)

    updated_at = Column(TIMESTAMP,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow,
                        nullable=False)

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

    def __repr__(self):
        return f'<User id={self.id} email_id={self.email}>'

    # Relationships
    login = relationship('Login',
                         backref=db.backref('user'),
                         uselist=False)

    user_notifications = relationship('UserNotification',
                                      backref=db.backref('user'))
    
    alerts = relationship('Alert', 
                          backref=db.backref('user'))

# Relationships on other tables
Address.user = relationship('User',
                            backref=db.backref('address'),
                            uselist=False)


##########################
### MARSHMALLOW SCHEMA ###
##########################


class UserSchema(SQLAlchemyAutoSchema):
    roles = fields.Method('get_roles',
                          dump_only=True)

    postal_code = fields.Method('get_postal_code',
                                dump_only=True)

    address = fields.Nested(AddressSchema(),
                            load_only=True)

# Marshmallow methods
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
