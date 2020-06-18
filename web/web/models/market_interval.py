from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class MarketInterval(Model):
    __tablename__ = 'market_intervals'
    
    market_interval_id = Column(db.Integer,
                                primary_key=True,
                                autoincrement=True,
                                nullable=False)

    market_id = Column(db.Integer, 
                       db.ForeignKey('markets.market_id'),
                       nullable=False)

    p_exp = Column(db.Float,
                   nullable=False)
    
    p_dev = Column(db.Float,
                   nullable=False)
    
    p_clear = Column(db.Float,
                   nullable=False)
    
    q_clear = Column(db.Float,
                     nullable=False)

    alpha = Column(db.Float,
                   nullable=False)

    start_time = Column(TIMESTAMP,
                        nullable=False)

    end_time = Column(TIMESTAMP,
                      nullable=False)
    
    # Relationships
    market = relationship('Market',
                          backref=db.backref('market_intervals'))

    def __repr__(self):
        return f'<MarketInterval market_interval_id={self.market_interval_id} market_id={self.market_id}>'
    
##########################
### MARSHMALLOW SCHEMA ###
##########################


class MarketIntervalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = MarketInterval
        load_instance = True
        include_fk = True