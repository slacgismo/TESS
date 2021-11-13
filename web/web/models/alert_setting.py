import enum
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.sql import label
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy import text, func
from sqlalchemy.orm import validates
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow import fields, ValidationError
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)
class AlertSetting(Model):
    __tablename__ = 'alert_setting'

    alert_setting_id = Column(db.Integer,
                           primary_key=True,
                           autoincrement=True,
                           nullable=False)

    utility_id = Column(db.Integer,
                        db.ForeignKey('utilities.utility_id'),
                        nullable=False)

    yellow_alarm_percentage = Column(db.Float, nullable=False)

    red_alarm_percentage = Column(db.Float, nullable=False)

    capacity_bound = Column(db.Float, nullable=False)

    resource_depletion = Column(db.Float, nullable=False)

    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'))

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Methods
    def __repr__(self):
        return f'<AlertSetting alert_setting_id={self.alert_setting_id} utility_id={self.utility_id} created_at={self.created_at} yellow_alarm_percentage={self.yellow_alarm_percentage} red_alarm_percentage={self.red_alarm_percentage} capacity_bound={self.capacity_bound} resource_depletion={self.resource_depletion}>'


##########################
### MARSHMALLOW SCHEMA ###
##########################


class AlertSettingSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = AlertSetting
        load_instance = True
        include_fk = True
