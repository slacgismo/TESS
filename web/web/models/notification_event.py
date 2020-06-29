import enum
from datetime import datetime
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import event

from web.emails.notification_emails import create_message, send_message
from web.models.notification_subscription import NotificationSubscription
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class ContextType(enum.Enum):
    TRANSFORMER = 'Transformer'
    FEEDER = 'Feeder'
    RETAIL_MARKET = 'Retail market'
    NONE = 'None'

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

    @event.listens_for(NotificationEvent, 'after_insert')
    def receive_after_insert(mapper, connection, target):
        'listens for a new notfication event inserted to database and sends notification email'

        # create appropriate notification message based on notification type
        if target.utility_notification_setting.notification_type.value == 'Resource':
            message = 'TESS is showing "battery" resource depleted.'
    
        elif target.utility_notification_setting.notification_type.value == 'Telecomm':
            message = 'TESS is observing a telecomm alert.'
    
        elif target.utility_notification_setting.notification_type.value == 'Price':
            message = f'TESS is observing a price alert at ${target.utility_notification_setting.limit}/MW.'

        elif target.utility_notification_setting.notification_type.value == 'Load Yellow' or target.utility_notification_setting.notification_type.value == 'Load Red':
            message = f'TESS {target.utility_notification_setting.notification_type.value} alert: {target.context} {target.context_id} is above {target.utility_notification_setting.limit}% capacity of the constraint at {target.created_at}.'
    
        elif target.utility_notification_setting.notification_type.value == 'Price Yellow' or target.utility_notification_setting.notification_type.value == 'Price Red':
            message = f'TESS {target.utility_notification_setting.notification_type.value} alert: {target.context} {target.context_id} is above {target.utility_notification_setting.limit}% of the alert price of the constraint at {target.created_at}.'
    
        elif target.utility_notification_setting.notification_type.value == 'Import Capacity':
            message = f'TESS System alert: {target.context} {target.context_id} is above {target.utility_notification_setting.limit} kW import capacity of the constraint at {target.created_at}.'
    
        elif target.utility_notification_setting.notification_type.value == 'Export Capacity':
            message = f'TESS System alert: {target.context} {target.context_id} is above {target.utility_notification_setting.limit} kW export capacity of the constraint at {target.created_at}.'

        # query all emails that have active subscriptions for the notification
        email_subscriptions = NotificationSubscription.query.filter(NotificationSubscription.utility_notification_setting_id==target.utility_notification_setting_id, NotificationSubscription.is_active==True).all()

        # send email notification to each email
        for email_subscription in email_subscriptions:
            send_message(service, email_subscription.email, message)




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
