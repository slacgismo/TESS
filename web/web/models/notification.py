from datetime import datetime
from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sqlalchemy.types import TIMESTAMP
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
    
    utility_id = Column(db.Integer,
                      db.ForeignKey('utilities.utility_id'),  
                      nullable=False)

    description = Column(db.Text,  
                         nullable=False)
    
    upper_limit = Column(db.Float,
                         nullable=False)

    lower_limit = Column(db.Float,
                         nullable=False)
    
    created_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow)

    updated_at = Column(TIMESTAMP, 
                        nullable=False, 
                        default=datetime.utcnow, 
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Notification notification_id={self.notification_id} description={self.description} utility_id={self.utility_id}>'


class NotificationTypeSchema(Schema):
    notification_type = fields.Str()
    label = fields.Str()
    is_active = fields.Bool()


class NotificationSchema(Schema):
    pk = fields.Str()
    email = fields.Str()
    notifications = fields.List(fields.Nested(NotificationTypeSchema))
