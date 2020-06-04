from datetime import datetime
from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class Tenant(Model):
    __tablename__ = 'tenant'

    tenant_id = Column(db.Integer,
                       autoincrement=True,
                       primary_key=True,
                       nullable=False)
    name = Column(db.String(128), nullable=False)
    created_at = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP,
                        nullable=False,
                        default=datetime.utcnow,
                        onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Tenant tenant_id={self.tenant_id} name={self.name}>'


class TenantSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = Tenant
