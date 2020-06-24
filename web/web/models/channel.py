import enum
from datetime import datetime
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy.types import TIMESTAMP

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class ChannelType(enum.Enum):
    #Two channel types: R for reverse, F for forward
    R = 'R'
    F = 'F'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type name.'''

        for channel_type in ChannelType:
            if channel_type.value == str_value:
                return channel_type

        return False

class Channel(Model):

    __tablename__ = 'channels'

    channel_id = Column(db.Integer, 
                        autoincrement=True, 
                        primary_key=True, 
                        nullable=False)

    meter_id = Column(db.Integer,  
                      db.ForeignKey('meters.meter_id'), 
                      nullable=False)

    setting = Column(db.Integer, 
                     nullable=False) 

    channel_type = Column(db.Enum(ChannelType), 
                          nullable=False)
    
    # Methods
    def __repr__(self):
        return f'<Channel channel_id={self.channel_id} meter_id={self.meter_id} channel_type={self.channel_type}>'
    

##########################
### MARSHMALLOW SCHEMA ###
##########################


class ChannelSchema(SQLAlchemyAutoSchema):
    channel_type = fields.Method('get_channel_type', deserialize='load_channel_type')
    
    def get_channel_type(self, obj):
        return obj.channel_type.value

    def load_channel_type(self, value):
        channel_enum = ChannelType.check_value(value)
        if not channel_enum:
            raise ValidationError(f'{value} is an invalid channel type')
        return channel_enum

    class Meta:
        model = Channel
        load_instance = True
        include_fk = True
        transient = True