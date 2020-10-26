import enum
from sqlalchemy.types import TIMESTAMP
from sqlalchemy import event, text, func
from marshmallow import fields, ValidationError
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from sendgrid.helpers.mail import Bcc
from web.emails.send_emails import send_email
from web.models.notification import Notification
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

    assigned_to = Column(db.String(255),
                         db.ForeignKey('users.email'),
                         nullable=False)

    description = Column(db.Text, nullable=False)

    status = Column(db.Enum(Status), nullable=False)

    context = Column(db.Enum(ContextType), nullable=False)

    context_id = Column(db.String(64), nullable=False)

    resolution = Column(db.Text, nullable=False)

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, server_default=func.now())

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

    def create_alert_notification_message(self):
        '''Returns tuple of alert type name and notification message for alert'''

        # Create appropriate notification message
        if self.alert_type.name.value == 'Resource':
            message = 'TESS is showing "battery" resource depleted.'

        elif self.alert_type.name.value == 'Telecomm':
            message = 'TESS is observing a telecomm alert.'

        elif self.alert_type.name.value == 'Price':
            message = f'TESS is observing a price alert at ${self.alert_type.limit}/MW.'

        elif self.alert_type.name.value == 'Load Yellow' \
            or self.alert_type.name.value == 'Load Red':
            message = f'TESS {self.alert_type.name.value} alert: {self.context.value} {self.context_id} is above {self.alert_type.limit}% capacity at {self.created_at}.'

        elif self.alert_type.name.value == 'Price Yellow' \
            or self.alert_type.name.value == 'Price Red':
            message = f'TESS {self.alert_type.name.value} alert: {self.context.value} {self.context_id} is above {self.alert_type.limit}% of the alert price at {self.created_at}.'

        elif self.alert_type.name.value == 'Import Capacity':
            message = f'TESS System alert: {self.context.value} {self.context_id} is above {self.alert_type.limit} kW import capacity at {self.created_at}.'

        elif self.alert_type.name.value == 'Export Capacity':
            message = f'TESS System alert: {self.context.value} {self.context_id} is above {self.alert_type.limit} kW export capacity at {self.created_at}.'

        return (self.alert_type.name.value, message)


@event.listens_for(Alert, 'after_insert')
def after_insert(mapper, connection, target):
    '''Sends email after a new alert event is inserted into database'''

    # Query all notifications that are active for the alert type
    notifications = Notification.query \
        .filter(Notification.alert_type_id==target.alert_type_id, Notification.is_active==True) \
            .all()

    # Checks if there are no notifications for early exit
    if len(notifications) == 0:
        return None

    alert = Alert.query \
        .filter_by(alert_id=target.alert_id) \
            .first()

    alert_type_name, message = alert.create_alert_notification_message()

    #Sends BCC emails to active notifications
    receiving_emails = [notification.email for notification in notifications]
    send_email(alert_type_name, message, receiving_emails)


##########################
### MARSHMALLOW SCHEMA ###
##########################


class AlertSchema(SQLAlchemyAutoSchema):
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
