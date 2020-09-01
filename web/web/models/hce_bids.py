from sqlalchemy.types import TIMESTAMP
from sqlalchemy import text, func
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class HceBids(Model):
    __tablename__ = 'hce_bids'
    bid_id = Column(db.Integer,
                    primary_key=True,
                    autoincrement=True,
                    nullable=False)
    start_time = Column(TIMESTAMP, nullable=False)
    end_time = Column(TIMESTAMP, nullable=False)
    p_bid = Column(db.Float, default=0, nullable=False)
    q_bid = Column(db.Float, default=0, nullable=False)
    is_supply = Column(db.Boolean(), default=True, nullable=False)
    comment = Column(db.String(512), nullable=False)
    market_id = Column(db.Integer,
                       db.ForeignKey('markets.market_id'),
                       nullable=False)
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))
    created_at = Column(TIMESTAMP, server_default=func.now())

    def __repr__(self):
        return f'<HceBids bid_id={self.bid_id}>'


class HceBidsSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = HceBids
        load_instance = True
        include_fk = True
