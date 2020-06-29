import enum
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.schema import UniqueConstraint
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError

from web.models.notification_subscription import NotificationSubscription
from web.models.notification_event import NotificationEvent
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class NotificationType(enum.Enum):
    YELLOW_ALARM_LOAD = 'Load Yellow'
    RED_ALARM_LOAD = 'Load Red'
    YELLOW_ALARM_PRICE = 'Price Yellow'
    RED_ALARM_PRICE = 'Price Red'
    PRICE_ALERTS = 'Price'
    IMPORT_CAPACITY = 'Import Capacity'
    EXPORT_CAPACITY = 'Export Capacity'
    RESOURCE_DEPLETION = 'Resource'
    TELECOMM_ALERTS = 'Telecomm'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type.'''

        for notification_type in NotificationType:
            if notification_type.value == str_value:
                return notification_type

        return False

class UtilityNotificationSetting(Model):
    __tablename__ = 'utility_notification_settings'

    utility_notification_setting_id = Column(db.Integer, 
                                             primary_key=True,
                                             autoincrement=True, 
                                             nullable=False)
    
    utility_id = Column(db.Integer,  
                        db.ForeignKey('utilities.utility_id'),  
                        nullable=False)

    notification_type = Column(db.Enum(NotificationType),
                               nullable=False)
    
    limit = Column(db.Float,
                   nullable=False)

    created_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow)
    
    updated_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Unique constraint for utility_id and notification_type
    __table_args__ = (UniqueConstraint('utility_id', 'notification_type', name='_utility_notification_uc'),
                     )

    # Relationships
    notification_subscriptions = relationship('NotificationSubscription',
                                             backref=db.backref('utility_notification_setting'))

    notification_events = relationship('NotificationEvent',
                                      backref=db.backref('utility_notification_setting'))

    # Methods
    def __repr__(self):
        return f'<UtilityNotificationSetting utility_notification_setting={self.utility_notification_setting_id} utility={self.utility_id} notification_type={self.notification_type} email={self.email} is_activ={self.is_active}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################

class UtilityNotificationSettingSchema(SQLAlchemyAutoSchema):
    notification_type = fields.Method('get_notification_type', deserialize='load_notification_type')

    def get_notification_type(self, obj):
        return obj.notification_type.value

    def load_notification_type(self, value):
        notification_enum = NotificationType.check_value(value)
        if not notification_enum:
            raise ValidationError(f'{value} is an invalid notification type')
        return notification_enum

    class Meta:
        model = UtilityNotificationSetting
        load_instance = True
        include_fk = True

class NotificationSubscriptionSchema(SQLAlchemyAutoSchema):
    notifications = fields.Nested(UtilityNotificationSettingSchema(only=('notification_type',)), dump_only=True)

    class Meta:
        model = NotificationSubscription
        load_instance = True
        include_fk = True