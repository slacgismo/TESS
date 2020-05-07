from flask_user import UserMixin

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class User(Model, UserMixin):

    __tablename__ = 'users'

    id = Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(db.String(50), unique=True, nullable=False)
    is_active = Column(db.Boolean(), nullable=False, server_default='0')
    first_name = Column(db.String(64), nullable=False)
    last_name = Column(db.String(64), nullable=False)

