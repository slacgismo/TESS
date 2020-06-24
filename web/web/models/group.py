from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.schema import UniqueConstraint
from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.role import Role, RoleSchema
from web.models.user import User, UserSchema
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Group(Model):
    __tablename__ = 'groups'

    group_id = Column(db.Integer,
                      primary_key=True,
                      autoincrement=True,
                      nullable=False)

    role_id = Column(db.Integer,
                     db.ForeignKey('roles.role_id'),
                     primary_key=True,
                     nullable=False)

    user_id = Column(db.Integer,
                     db.ForeignKey('users.id'), 
                     primary_key=True,
                     nullable=False)

    is_active = Column(db.Boolean(), 
                       default=False, 
                       nullable=False)

    is_archived = Column(db.Boolean(), 
                         default=False, 
                         nullable=False)

    created_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow)
                        
    updated_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)
    
    # Unique constraint for role_id and user_id
    __table_args__ = (UniqueConstraint('role_id', 'user_id', name='_role_user_uc'),
                     )

    # Methods
    def __repr__(self):
        return f'<Group group_id={self.group_id} role_id={self.role_id} user_id={self.user_id}>'

# Relationships on other tables
Role.groups = db.relationship('Group',
                              backref=db.backref('role'))

User.groups = db.relationship('Group',
                              backref=db.backref('user'))


##########################
### MARSHMALLOW SCHEMA ###
##########################


class GroupSchema(SQLAlchemyAutoSchema):
    role = fields.Nested(RoleSchema(only=('name', )), dump_only=True)
    user = fields.Nested(UserSchema(only=('email', )), dump_only=True)

    class Meta:
        model = Group
        include_fk = True
        load_instance = True
