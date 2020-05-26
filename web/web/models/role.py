import enum
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

    role_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    name = Column(db.Enum(RoleType), unique=True, nullable=False)