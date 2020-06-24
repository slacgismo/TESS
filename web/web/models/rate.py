from sqlalchemy.types import TIMESTAMP
from datetime import datetime

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class Rate(Model):
    __tablename__ = 'rates'

    rate_id = Column(db.Integer,
                     primary_key=True,
                     autoincrement=True,
                     nullable=False)

    description = Column(db.Text, 
                         nullable=False)

    # Methods
    def __repr__(self):
        return f'<Rate rate_id={self.rate_id} description={self.description}>'
