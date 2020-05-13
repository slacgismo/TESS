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