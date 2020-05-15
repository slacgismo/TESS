from marshmallow import Schema, fields
#from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
# from sqlalchemy.types import TIMESTAMP
# from web.database import (
#     db,
#     Model,
#     Column,
#     SurrogatePK,
#     relationship,
#     reference_col,
# )


# class Alert(Model):
#     __tablename__ = 'alerts'

#     def __repr__(self):
#         return f'<Alert>'


class AlertSchema(Schema):
    date = fields.Str()
    time = fields.Str()
    alert_type = fields.Str()
    description = fields.Str()
    status = fields.Str()
    assigned_to = fields.Str()
    resolution = fields.Str()
