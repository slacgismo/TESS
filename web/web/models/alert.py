import enum
from datetime import datetime
from marshmallow import fields, ValidationError
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

class Status(enum.Enum):
    OPEN = 'open'
    PENDING = 'pending'
    RESOLVED = 'resolved'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type.'''

        for status in Status:
            if status.value == str_value:
                return status

        return False

class AssignedToOptions(enum.Enum):
    OPERATOR_1 = 'operator 1'
    OPERATOR_2 = 'operator 2'
    FIELD_CREW = 'field crew'
    AUTOMATED_SYSTEM = 'automated system'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type.'''

        for assigned_to_option in AssignedToOptions:
            if assigned_to_option.value == str_value:
                return assigned_to_option

        return False

class ContextType(enum.Enum):
    TRANSFORMER = 'Transformer'
    FEEDER = 'Feeder'
    RETAIL_MARKET = 'Retail market'
    NONE = 'None'

    @staticmethod
    def check_value(str_value):
        '''Takes in string value, returns False if it isn't an accepted enum value, else returns enum type.'''

        for context_type in ContextType:
            if context_type.value == str_value:
                return context_type

        return False

class Alert(Model):
    __tablename__ = 'alerts'

    alert_id = Column(db.Integer, 
                      primary_key=True,
                      autoincrement=True, 
                      nullable=False)
    
    alert_type_id = Column(db.Integer, 
                        db.ForeignKey('alert_types.alert_type_id'), 
                        nullable=False)
    
    assigned_to = Column(db.Enum(AssignedToOptions),  
                         nullable=False)

    description = Column(db.Text,
                         nullable=False)

    status = Column(db.Enum(Status),
                    nullable=False)

    context = Column(db.Enum(ContextType),
                     nullable=False)

    context_id = Column(db.String(64),
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
        return f'<Alert alert_id={self.alert_id} alert_type_id={self.alert_type_id} created_at={self.created_at}>'

    def get_filter_type(self):
        '''Returns filter type as a string for alert frontend set-up'''

        if self.alert_type.name.value == 'Import Capacity' \
            or self.alert_type.name.value == 'Export Capacity' \
                or self.alert_type.name.value == 'Load Yellow' \
                    or self.alert_type.name.value == 'Load Red':
            return 'Capacity bounds'
        
        if self.alert_type.name.value == 'Price Yellow' \
            or self.alert_type.name.value == 'Price Red' \
                or self.alert_type.name.value == 'Price':
            return 'Price alerts'
        
        if self.alert_type.name.value == 'Telecomm':
            return 'Telecomm alerts'
        
        if self.alert_type.name.value == 'Resource':
            return 'Resource depletion'
        
        if self.alert_type.name.value == 'Peak Event':
            return 'Peak event'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class AlertSchema(SQLAlchemyAutoSchema):
    assigned_to = fields.Method('get_assigned_to', deserialize='load_assigned_to')
    alert_type = fields.Method('get_alert_type', dump_only=True)
    date = fields.Method('get_date_format', dump_only=True)
    time = fields.Method('get_time_format', dump_only=True)
    status = fields.Method('get_status', deserialize='load_status')
    context = fields.Method(deserialize='load_context_type')

    def get_alert_type(self, obj):
        return obj.get_filter_type()

    def get_date_format(self, obj):
        return str(obj.created_at.date())
    
    def get_time_format(self, obj):
        return str(obj.created_at.time())

    def get_assigned_to(self, obj):
        return obj.assigned_to.value

    def load_assigned_to(self, value):
        assigned_to_enum = AssignedToOptions.check_value(value)
        if not assigned_to_enum:
            raise ValidationError(f'{value} is an invalid Assigned To Option')
        return assigned_to_enum

    def get_status(self, obj):
        return obj.status.value

    def load_status(self, value):
        status_enum = Status.check_value(value)
        if not status_enum:
            raise ValidationError(f'{value} is an invalid Status')
        return status_enum

    def load_context_type(self, value):
        context_type_enum = ContextType.check_value(value)
        if not context_type_enum:
            raise ValidationError(f'{value} is an invalid Context Type')
        return context_type_enum

    class Meta:
        model = Alert
        load_instance = True
        include_fk = True