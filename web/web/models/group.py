from sqlalchemy.types import TIMESTAMP
from datetime import datetime
from flask_login import UserMixin
from web.models.role import Role
from web.models.user import User
from web.models.utility import Utility
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Group(UserMixin, Model):
    __tablename__ = 'groups'

    group_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)

    role_id = Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    user_id = Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    utility_id = Column(db.Integer, db.ForeignKey('utilities.utility_id'))

    is_active = Column(db.Boolean(False), nullable=False)
    is_archived = Column(db.Boolean(False), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    utility = relationship('Utility', backref=db.backref('groups'))
    role = db.relationship('Role', backref=db.backref('groups', lazy='dynamic'))
    user = db.relationship('User', backref=db.backref('groups', lazy='dynamic'))

    # def can(self, permission):
    #     return self.role is not None and self.role.has_permission(permission)