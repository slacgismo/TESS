from flask_user import UserMixin
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text, func
from marshmallow import fields
from sqlalchemy.schema import UniqueConstraint
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.notification import Notification
from web.models.login import Login, LoginSchema
from web.models.alert import Alert
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
    email = Column(db.String(255), unique=True, nullable=False)

    email_confirmed_at = Column(TIMESTAMP)

    # User information
    first_name = Column(db.String(64), nullable=False)

    last_name = Column(db.String(64), nullable=False)

    address_id = Column(db.Integer,
                        db.ForeignKey('addresses.address_id'),
                        nullable=False)

    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),
                        nullable=False)

    is_active = Column(db.Boolean(), default=False, nullable=False)

    is_archived = Column(db.Boolean(), default=False, nullable=False)

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, server_default=func.now())

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
    login = relationship('Login', backref=db.backref('user'), uselist=False)

    notifications = relationship('Notification', backref=db.backref('user'))

    alerts = relationship('Alert', backref=db.backref('user'))


##########################
### MARSHMALLOW SCHEMA ###
##########################


class UserSchema(SQLAlchemyAutoSchema):
    roles = fields.Method('get_roles', dump_only=True)
    postal_code = fields.Method('get_postal_code', dump_only=True)
    login = fields.Nested(LoginSchema(), dump_only=True)

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

