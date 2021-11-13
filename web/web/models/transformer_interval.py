from sqlalchemy.types import TIMESTAMP
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from web.models.transformer import Transformer
from web.database import (
    db,
    Model,
    Column,
    SurrogatePK,
    relationship,
    reference_col,
)


class TransformerInterval(Model):
    __tablename__ = 'transformer_intervals'

    transformer_interval_id = Column(db.Integer,
                                primary_key=True,
                                autoincrement=True,
                                nullable=False)

    transformer_id = Column(db.Integer,
                       db.ForeignKey('transformers.transformer_id'),
                       nullable=False)

    import_capacity = Column(db.Float, nullable=False)

    export_capacity = Column(db.Float, nullable=True)

    q = Column(db.Float, nullable=True)

    unresp_load = Column(db.Float, nullable=True)

    start_time = Column(TIMESTAMP, nullable=True)

    end_time = Column(TIMESTAMP, nullable=True)

    # Methods
    def __repr__(self):
        return f'<TransformerInterval transformer_interval_id={self.transformer_interval_id} transformer_id={self.transformer_id}>'

    # Relationships
    transformer = relationship('Transformer', backref=db.backref('transformer_intervals'))


##########################
### MARSHMALLOW SCHEMA ###
##########################


class TransformerIntervalSchema(SQLAlchemyAutoSchema):
    class Meta:
        model = TransformerInterval
        load_instance = True
        include_fk = True
