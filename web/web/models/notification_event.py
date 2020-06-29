import enum
from datetime import datetime
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.types import TIMESTAMP
#from sqlalchemy import event

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class ContextType(enum.Enum):
    TRANSFORMER = 'transformer'
    FEEDER = 'feeder'
    RETAIL_MARKET = 'retail market'

class NotificationEvent(Model):
    __tablename__ = 'notification_events'

    notification_event_id = Column(db.Integer, 
                                   primary_key=True,
                                   autoincrement=True, 
                                   nullable=False)
    
    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),  
                      nullable=False)

    utility_notification_setting_id = Column(db.Integer,
                                             db.ForeignKey('utility_notification_settngs.utility_notification_setting_id'),  
                                             nullable=False)
    context = Column(db.Enum(ContextType),  
                     nullable=False)
    
    context_id = Column(db.String(64),
                        nullable=False)

    created_by = Column(db.Float,
                         nullable=False)
    
    created_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow)

    # Methods
    def __repr__(self):
        return f'<NotificationEvent notification_event_id={self.notification_event_id} utility={self.utility_id} utility_notification_setting_id={self.utility_notification_setting_id} created_at={self.created_at}>'


# # standard decorator style
# @event.listens_for(Notification, 'after_insert')
# def receive_after_insert(mapper, connection, target):
#     "listen for the 'after_insert' event"
    
#     # ... (event handling logic) ...

##########################
### MARSHMALLOW SCHEMA ###
##########################


class NotificationTypeSchema(Schema):
    notification_type = fields.Str()
    label = fields.Str()
    is_active = fields.Bool()


class NotificationSchema(Schema):
    pk = fields.Str()
    email = fields.Str()
    notifications = fields.List(fields.Nested(NotificationTypeSchema))
