import enum
from flask_login import UserMixin
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
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type name.'''
 
        for role_type in RoleType:
            if role_type.value == str_value:
                return role_type
        
        return False

class Role(UserMixin, Model):
    __tablename__ = 'roles'

    role_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    role_type = Column(db.Enum(RoleType), nullable=False, unique=True)
    # permissions = db.Column(db.Integer)

    # def add_permission(self, permission):
    #     if not self.has_permission(permission):
    #         self.permissions += permission
    
    # def remove_permission(self, permission):
    #     if self.has_permission(permission):
    #         self.permissions -= permission
    
    # def reset_permission(self):
    #     self.permissions = 0
    
    # def has_permission(self, permission):
    #     return self.permissions & permission == permission