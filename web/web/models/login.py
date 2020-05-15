from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from flask_user import UserMixin
from web.models.user import User
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Login(Model, UserMixin):
    __tablename__ = 'logins'

    login_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(db.Integer, db.ForeignKey('users.user_id'), ondelete='CASCADE', nullable=False)
    
    username = Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship('User', uselist=False, foreign_keys=user_id, backref=db.backref('login'))

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)