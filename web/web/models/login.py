from werkzeug.security import generate_password_hash, check_password_hash
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


class Login(Model):
    __tablename__ = 'logins'

    login_id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(db.String(100), db.ForeignKey('users.user_id'), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))

    #one-to-one relationship with user
    username = relationship('User', backref=db.backref('logins'), uselist=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)