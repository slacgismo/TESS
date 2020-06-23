from datetime import datetime, timedelta
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from web.models.home_hub import HomeHub
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class Market(Model):
    __tablename__ = 'markets'

    market_id = Column(db.Integer, 
                       primary_key=True, 
                       autoincrement=True, 
                       nullable=False)

    source = Column(db.Text,
                    nullable=False)

    ts = Column(db.Float,
                nullable=False)

    p_max = Column(db.Float,
                 nullable=False)
    
    is_active = Column(db.Boolean,
                     default=False,
                     nullable=False)

    is_archived = Column(db.Boolean,
                       default=False,
                       nullable=False)

    created_at = Column(TIMESTAMP, 
                        default=datetime.utcnow,
                        nullable=False)

    updated_at = Column(TIMESTAMP,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow,
                        nullable=False)

    def __repr__(self):
        return f'<Market market_id={self.market_id} p_max={self.p_max} created_at={self.created_at}>'

#Relationships

home_hubs = relationship('HomeHub',
                         backref=db.backref('market'))

##########################
### MARSHMALLOW SCHEMA ###
##########################

class MarketSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Market
        load_instance = True
        include_fk = True