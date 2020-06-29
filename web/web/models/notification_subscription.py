from datetime import datetime
from sqlalchemy.types import TIMESTAMP

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class NotificationSubscription(Model):
    __tablename__ = 'notification_subscriptions'

    notification_subscription_id = Column(db.Integer, 
                                          primary_key=True,
                                          autoincrement=True, 
                                          nullable=False)
    
    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),  
                      nullable=False)

    utility_notification_setting_id = Column(db.Integer,
                                             db.ForeignKey('utility_notification_settings.utility_notification_setting_id'),  
                                             nullable=False)
    
    email = Column(db.String(255),
                   nullable=False)

    is_active = Column(db.Boolean,
                       default=False,
                       nullable=False)

    created_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow)
    
    updated_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Methods
    def __repr__(self):
        return f'<NotificationSubscription notification_subscription_id={self.notification_subscription_id} utility={self.utility_id} utility_notification_setting_id={self.utility_notification_setting_id} email={self.email} is_active={self.is_active}>'