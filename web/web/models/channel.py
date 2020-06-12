from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy import ForeignKeyConstraint
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

class Channel(Model):

    __tablename__ = 'channels'

    channel_id = Column(db.Integer, autoincrement=True, primary_key=True, nullable=False)
    meter_id = Column(db.Integer,  db.ForeignKey('meters.meter_id'), nullable=False)
    setting = Column(db.Integer, nullable = False) 
    channel_type = Column(db.String(64), nullable=False)
    
    def __repr__(self):
        return f'<Channel channel_id={self.channel_id} meter_id={self.meter_id} channel_type={self.channel_type}>'
    

##########################
### MARSHMALLOW SCHEMA ###
##########################

class ChannelSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Channel
        load_instance = True
        include_fk = True