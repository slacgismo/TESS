from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text, func
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError
from flask_user import UserMixin
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Login(UserMixin, Model):
    __tablename__ = 'logins'

    login_id = Column(db.Integer,
                      primary_key=True,
                      autoincrement=True,
                      nullable=False)

    user_id = Column(db.Integer,
                     db.ForeignKey('users.id'),
                     unique=True,
                     nullable=False)

    username = Column(db.String(50), unique=True, nullable=False)

    password_hash = db.Column(db.String(128))

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Methods
    def __repr__(self):
        return f'<Login login_id={self.login_id} user_id={self.user_id} updated_at={self.updated_at}>'

    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute.')

    @password.setter
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        is_correct_password = check_password_hash(self.password_hash, password)
        if not is_correct_password:
            raise ValueError('Incorrect Password')
        return is_correct_password


##########################
### MARSHMALLOW SCHEMA ###
##########################


class LoginSchema(SQLAlchemyAutoSchema):
    password_hash = fields.Method(deserialize='create_password_hash')

    # Marshmallow methods
    def create_password_hash(self, obj):
        password_hash = generate_password_hash(obj)
        return password_hash

    class Meta:
        model = Login
        load_instance = True
        include_fk = True
