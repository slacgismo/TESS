import enum
from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class RoleType(enum.Enum):
    MEMBER = 'member'
    OPERATOR = 'operator'
    SUPERUSER = 'superuser'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type.'''

        for role_type in RoleType:
            if role_type.value == str_value:
                return role_type

        return False


class Role(Model):
    __tablename__ = 'roles'

    role_id = Column(db.Integer,
                     primary_key=True,
                     autoincrement=True,
                     nullable=False)

    name = Column(db.Enum(RoleType), unique=True, nullable=False)

    # Methods
    def __repr__(self):
        return f'<Role role_id={self.role_id} name={self.name}>'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class RoleSchema(SQLAlchemyAutoSchema):
    name = fields.Method('get_role_name', deserialize='load_role_type')

    def get_role_name(self, obj):
        return obj.name.value

    def load_role_type(self, value):
        role_enum = RoleType.check_value(value)
        if not role_enum:
            raise ValidationError(f'{value} is an invalid role type')
        return role_enum

    class Meta:
        model = Role
        include_fk = True
        load_instance = True
        transient = True
