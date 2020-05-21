import enum
from flask_user import UserMixin
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

class Role(Model):
    __tablename__ = 'roles'

    role_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    role_type = Column(db.Enum(RoleType), nullable=False)
    permissions = db.Column(db.Integer)

    def add_permission(self, permission):
        if not self.has_permission(permission):
            self.permissions += permission
    
    def remove_permission(self, permission):
        if self.has_permission(permission):
            self.permissions -= permission
    
    def reset_permission(self):
        self.permissions = 0
    
    def has_permission(self, permission):
        return self.permissions & permission == permission