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
    YELLOW_ALARM_LOAD = 'Yellow Alarm (Load)'
    RED_ALARM_LOAD = 'Red Alarm (Load)'
    YELLOW_ALARM_PRICE = 'Yellow Alarm (Price)'
    RED_ALARM_PRICE = 'Red Alarm (Price)'
    PRICE_ALERTS = 'Price Alerts'
    CAPACITY_BOUNDS = 'Capacity Bounds'
    RESOURCE_DEPLETION = 'Resource Depletion'
    TELECOMM_ALERTS = 'Telecomm Alerts'

class UtilityNotificationSetting(Model):
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

    # Methods
    def __repr__(self):
        return f'<UtilityNotificationSetting utility_notification_setting={self.utility_notification_setting_id} utility={self.utility_id} notification_type={self.notification_type} email={self.email} is_activ={self.is_active}>'