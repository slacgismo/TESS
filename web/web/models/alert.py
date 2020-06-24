import enum
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

class AlertType(enum.Enum):
    CAPACITY_BOUNDS = 'capacity bounds'
    PRICE_ALERTS = 'price alerts'
    TELECOMM_ALERTS = 'telecomm alerts'
    RESOURCE_DEPLETION = 'resource depletion'

class Status(enum.Enum):
    OPEN = 'open'
    PENDING = 'pending'
    RESOLVED = 'resolved'

class Alert(Model):
    __tablename__ = 'alerts'

    alert_id = Column(db.Integer, 
                      primary_key=True,
                      autoincrement=True, 
                      nullable=False)
    
    utility_id = Column(db.Integer, 
                        db.ForeignKey('utilities.utility_id'), 
                        nullable=False)
    
    user_id = Column(db.Integer,
                     db.ForeignKey('users.user_id'),  
                     nullable=False)

    notification_id = Column(db.Integer,
                             db.ForeignKey('notifications.notification_id'),
                             nullable=False)

    alert_type = Column(db.Enum(AlertType),
                        nullable=False)

    description = Column(db.Text,
                         nullable=False)

    status = Column(db.Enum(Status),
                    nullable=False)

    resolution = Column(db.Text,
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
        return f'<Alert alert_id={self.alert_id} alert_type={self.alert_type} status={self.status}>'
   

##########################
### MARSHMALLOW SCHEMA ###
##########################


class AlertSchema(Schema):
    date = fields.Str()
    time = fields.Str()
    alert_type = fields.Str()
    description = fields.Str()
    status = fields.Str()
    assigned_to = fields.Str()
    resolution = fields.Str()

