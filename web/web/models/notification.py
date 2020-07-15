from itertools import chain
from sqlalchemy import text, func
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

    email = Column(db.String(255), nullable=False)

    is_active = Column(db.Boolean, default=False, nullable=False)

    created_by = Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Unique constraint for alert_type_id and email
    __table_args__ = (UniqueConstraint('alert_type_id',
                                       'email',
                                       name='_alert_type_id_email_uc'), )

    # Methods
    def __repr__(self):
        return f'<Notification notification_id={self.notification_id} alert_type_id={self.alert_type_id} is_active={self.is_active}>'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class NotificationSchema(SQLAlchemyAutoSchema):
    pk = fields.Method('get_id')
    notification_type = fields.Method('get_notification_type')
    label = fields.Method('get_label')

    def get_notification_type(self, obj):
        return str(obj.alert_type.name.name)

    def get_label(self, obj):
        return obj.alert_type.name.value

    def get_id(self, obj):
        return obj.notification_id

    class Meta:
        model = Notification
        load_instance = True
        include_fk = True
