from marshmallow import Schema, fields
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
# from sqlalchemy.types import TIMESTAMP
# from web.database import (
#     db,
#     Model,
#     Column,
#     SurrogatePK,
#     relationship,
#     reference_col,
# )

# class Notification(Model):
#     __tablename__ = 'notification'

# def __repr__(self):
#     return f'<Notification>'


class NotificationTypeSchema(Schema):
    notification_type = fields.Str()
    label = fields.Str()
    is_active = fields.Bool()


class NotificationSchema(Schema):
    pk = fields.Str()
    email = fields.Str()
    notifications = fields.List(fields.Nested(NotificationTypeSchema))
