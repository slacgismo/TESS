from datetime import datetime
from itertools import chain
from sqlalchemy import func
from sqlalchemy.sql import label
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.schema import UniqueConstraint
from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class Notification(Model):
    __tablename__ = 'notifications'

    notification_id = Column(db.Integer, 
                             primary_key=True,
                             autoincrement=True, 
                             nullable=False)
    
    alert_type_id = Column(db.Integer,
                           db.ForeignKey('alert_types.alert_type_id'),  
                           nullable=False)

    email = Column(db.String(255),
                   nullable=False)

    is_active = Column(db.Boolean,
                       default=False,
                       nullable=False)

    created_by = Column(db.Integer,
                        db.ForeignKey('users.id'),
                        nullable=False)

    created_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow)
    
    updated_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    # Unique constraint for alert_type_id and email
    __table_args__ = (UniqueConstraint('alert_type_id', 'email', name='_alert_type_id_email_uc'),
                     )

    # Methods
    def __repr__(self):
        return f'<Notification notification_id={self.notification_id} alert_type_id={self.alert_type_id} is_active={self.is_active}>'

    def get_all_notifications_per_email(self):
        '''Returns list of all notifications with same email'''
        
        notifications_per_email = Notification.query.filter_by(email=self.email).all()
        return notifications_per_email

    @classmethod
    def get_one_notification_id_per_email(cls):
        '''Returns list of one notification id per unique email'''

        # group by emails, with the minimum notification id in order to eliminate repeating email rows on frontend
        notification_ids_grouped_by_email = cls.query \
                                                .with_entities(label('notification_id', func.min(cls.notification_id))) \
                                                .group_by(cls.email) \
                                                .all()

        #unpack tuple to flattened list of ids
        notification_ids = list(chain(*notification_ids_grouped_by_email)) 

        return notification_ids
    

##########################
### MARSHMALLOW SCHEMA ###
##########################


class NotificationSchema(SQLAlchemyAutoSchema):
    # NOTE: pk field to fit in with current test data implementation,
    # however this set up is not an accurate representation of notification pks
    pk = fields.Function(lambda obj: obj.notification_id)
    notifications = fields.Method('get_notifications')

    def get_notifications(self, obj):
        notifications = obj.get_all_notifications_per_email()
        notification_list = []

        for notification in notifications:
            notification_info = {"notification_type": str(notification.alert_type.name.name),
                                 "label": notification.alert_type.name.value,
                                 "is_active": notification.is_active}
            notification_list.append(notification_info)
        return notification_list

    class Meta:
        model = Notification
        load_instance = True
        include_fk = True