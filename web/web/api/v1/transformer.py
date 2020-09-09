from web.database import db
from flask import request, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .response_wrapper import ApiResponseWrapper
from web.models.transformer import Transformer, TransformerSchema

transformer_api_bp = Blueprint('transformer_api_bp', __name__)


@transformer_api_bp.route('/transformers', methods=['GET'])
def get_transformers():
    '''
    Get transformers
    '''
    arw = ApiResponseWrapper()

    # get the list fields we want on the response
    fields_to_filter_on = request.args.getlist('fields')

    # validate that they exist
    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Transformer.__table__.columns:
                arw.add_errors({field: 'Invalid Transfomer field'})
                return arw.to_json(None, 400)
    else:
        # make sure we get everything if no fields are given
        fields_to_filter_on = None

    transformer_schema = TransformerSchema(only=fields_to_filter_on)
    transformers = Transformer.query.all()
    results = transformer_schema.dump(transformers, many=True)

    return arw.to_json(results)


@transformer_api_bp.route('/transformer/<int:transformer_id>', methods=['GET'])
def show_transformer_info(transformer_id):
    '''
    Returns transformer
    '''

    arw = ApiResponseWrapper()
    transformer_schema = TransformerSchema()

    try:
        t = Transformer.query.filter_by(transformer_id=transformer_id).one()
    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')
        return arw.to_json(None, 400)

    results = transformer_schema.dump(t)

    return arw.to_json(results)


@transformer_api_bp.route('/transformer/<int:transformer_id>', methods=['PUT'])
def update_transformer(transformer_id):
    '''
    Updates transformer in database
    '''

    arw = ApiResponseWrapper()
    transformer_schema = TransformerSchema(
        exclude=['created_at', 'updated_at'])
    modified_transformer = request.get_json()

    try:
        Transformer.query.filter_by(transformer_id=transformer_id).one()
        modified_transformer = transformer_schema.load(modified_transformer,
                                                       session=db.session)
        db.session.commit()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = transformer_schema.dump(modified_transformer)

    return arw.to_json(results)


@transformer_api_bp.route('/transformer', methods=['POST'])
def add_transformer():
    '''
    Adds new transformer to database
    '''

    arw = ApiResponseWrapper()
    transformer_schema = TransformerSchema(
        exclude=['transformer_id', 'created_at', 'updated_at'])
    transformer_json = request.get_json()

    try:
        new_transformer = transformer_schema.load(transformer_json,
                                                  session=db.session)
        db.session.add(new_transformer)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = TransformerSchema().dump(new_transformer)

    return arw.to_json(result)
