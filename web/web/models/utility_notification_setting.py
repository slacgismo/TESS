import enum
from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.schema import UniqueConstraint

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

class UtilityConstraintSetting(Model):
    __tablename__ = 'utility_notification_setting'

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

    notification_subscriptions = relationship('NotificationSubscription',
                                             backref=db.backref('utility_notification_setting'))

    notification_events = relationship('NotificationEvent',
                                      backref=db.backref('utility_notification_setting'))

    # Methods
    def __repr__(self):
        return f'<UtilityNotificationSetting utility_notification_setting={self.utility_notification_setting_id} utility={self.utility_id} notification_type={self.notification_type} email={self.email} is_activ={self.is_active}>'