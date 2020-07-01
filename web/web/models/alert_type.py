import enum
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import text, func
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError

from web.models.notification import Notification
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)

class AlertName(enum.Enum):
    YELLOW_ALARM_LOAD = 'Load Yellow'
    RED_ALARM_LOAD = 'Load Red'
    YELLOW_ALARM_PRICE = 'Price Yellow'
    RED_ALARM_PRICE = 'Price Red'
    PRICE_ALERT = 'Price'
    IMPORT_CAPACITY = 'Import Capacity'
    EXPORT_CAPACITY = 'Export Capacity'
    RESOURCE_DEPLETION = 'Resource'
    TELECOMM_ALERT = 'Telecomm'
    PEAK_EVENT = 'Peak Event'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type.'''

        for alert_name in AlertName:
            if alert_name.value == str_value:
                return alert_name

        return False

class AlertType(Model):
    __tablename__ = 'alert_types'

    alert_type_id = Column(db.Integer, 
                           primary_key=True,
                           autoincrement=True, 
                           nullable=False)
    
    utility_id = Column(db.Integer,  
                        db.ForeignKey('utilities.utility_id'),  
                        nullable=False)

    name = Column(db.Enum(AlertName),
                          nullable=False)
    
    limit = Column(db.Float,
                   nullable=False)

    updated_at = Column(TIMESTAMP, 
                        nullable=False,
                        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP,
                        nullable=False,
                        server_default=func.now())

    # Unique constraint for utility_id and name
    __table_args__ = (UniqueConstraint('utility_id', 'name', name='_utility_name_uc'),
                     )

    # Relationships
    notifications = relationship('Notification',
                                 backref=db.backref('alert_type'))

    # Methods
    def __repr__(self):
        return f'<AlertType alert_type_id={self.alert_type_id} utility_id={self.utility_id} name={self.name}>'

##########################
### MARSHMALLOW SCHEMA ###
##########################
class AlertTypeSchema(SQLAlchemyAutoSchema):
    name = fields.Method('get_alert_name', deserialize='load_alert_name')

    def get_alert_name(self, obj):
        return obj.name.value

    def load_alert_name(self, value):
        name_enum = AlertName.check_value(value)
        if not name_enum:
            raise ValidationError(f'{value} is an invalid alert name')
        return name_enum

    class Meta:
        model = AlertType
        load_instance = True
        include_fk = True