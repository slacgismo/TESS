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

class UserNotification(Model):
    __tablename__ = 'user_notifications'

    user_notification_id = Column(db.Integer,
                                  primary_key=True,
                                  autoincrement=True,
                                  nullable=False)

    user_id = Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    notification_id = Column(db.Integer,
                        db.ForeignKey('notifications.notification_id'),
                        nullable=False)

    email = Column(db.String(255),
                   nullable=False)

    is_active = Column(db.Boolean(),
                       default=False,
                       nullable=False)

    created_at = Column(TIMESTAMP,
                        default=datetime.utcnow,
                        nullable=False)

    updated_at = Column(TIMESTAMP,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow,
                        nullable=False)

    # Methods
    def __repr__(self):
        return f'<UserNotification user_notification_id={self.user_notification_id} user_id={self.user_id} notification_id={self.notification_id}>'