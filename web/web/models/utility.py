from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.types import TIMESTAMP
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Utility(Model):
    __tablename__ = 'utilities'

    utility_id = Column(db.Integer,
                        primary_key=True, 
                        autoincrement=True, 
                        nullable=False)

    name = Column(db.String(64),
                  nullable=False)

    subscription_start = Column(TIMESTAMP,
                                nullable=False)
    
    subscription_end = Column(TIMESTAMP,
                              nullable=False)

    def __repr__(self):
        return f'<Utility utility_id={self.utility_id} name={self.name}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################

class UtilitySchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Utility
        include_fk = True
        load_instance = True
