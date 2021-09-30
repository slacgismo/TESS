import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.transformer_interval import TransformerInterval, TransformerIntervalSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

transformer_interval_api_bp = Blueprint('transformer_interval_api_bp', __name__)


@transformer_interval_api_bp.route('/transformer_intervals', methods=['GET'])
def get_transformer_intervals():
    '''
    Returns transformer intervals
    '''

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')
    start_time = request.args.get('start_time', None)
    end_time = request.args.get('end_time', None)
    transformer_id = request.args.get('transformer_id', None)

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in TransformerInterval.__table__.columns:
                arw.add_errors({field: 'Invalid transformer Interval field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    transformer_interval_schema = TransformerIntervalSchema(only=fields_to_filter_on)

    ti = TransformerInterval.query.filter()

    try:
        if start_time:
            start_time = parser.parse(start_time)
            ti = ti.filter(TransformerInterval.start_time >= start_time)
        if end_time:
            end_time = parser.parse(end_time)
            ti = ti.filter(TransformerInterval.end_time <= end_time)
        if transformer_id:
            transformer_id = int(transformer_id)
            ti = ti.filter(TransformerInterval.transformer_id == transformer_id)

    except parser.ParserError as pe:
        arw.add_errors(
            'Could not parse the date time value. Please provide a valid format.'
        )
        return arw.to_json(None, 400)

    except ValueError as ve:
        arw.add_errors(
            'Could not parse the transformer id. It should be an integer.')
        return arw.to_json(None, 400)

    results = transformer_interval_schema.dump(ti, many=True)

    return arw.to_json(results)


@transformer_interval_api_bp.route('/transformer_interval/<int:transformer_interval_id>',
                              methods=['GET'])
def show_transformer_interval_info(transformer_interval_id):
    '''
    Returns transformer interval information as json object
    '''

    arw = ApiResponseWrapper()
    transformer_schema = TransformerIntervalSchema()

    try:
        transformer_interval = TransformerInterval.query.filter_by(
            transformer_interval_id=transformer_interval_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = transformer_schema.dump(transformer_interval)

    return arw.to_json(results)


@transformer_interval_api_bp.route('/transformer_interval/latest',
                              methods=['GET'])
def show_latest_transformer_interval_info():
    '''
    Returns latest transformer interval information as json object
    '''

    arw = ApiResponseWrapper()
    transformer_schema = TransformerIntervalSchema()

    try:
        transformer_interval = TransformerInterval.query.order_by(desc('transformer_interval_id')).first()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = transformer_schema.dump(transformer_interval)

    return arw.to_json(results)


@transformer_interval_api_bp.route('/transformer_interval/<int:transformer_interval_id>',
                              methods=['PUT'])
def update_transformer_interval(transformer_interval_id):
    '''
    Updates transformer interval in database
    '''

    arw = ApiResponseWrapper()
    transformer_interval_schema = TransformerIntervalSchema()
    modified_transformer_interval = request.get_json()

    try:
        TransformerInterval.query.filter_by(
            transformer_interval_id=transformer_interval_id).one()
        modified_transformer_interval = transformer_interval_schema.load(
            modified_transformer_interval, session=db.session)
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

    results = transformer_interval_schema.dump(modified_transformer_interval)

    return arw.to_json(results)


@transformer_interval_api_bp.route('/transformer_interval', methods=['POST'])
def add_transformer_interval():
    '''
    Adds new transformer interval to database
    '''

    arw = ApiResponseWrapper()
    transformer_interval_schema = TransformerIntervalSchema(
        exclude=['transformer_interval_id'])
    transformer_interval_json = request.get_json()

    try:
        new_transformer_interval = transformer_interval_schema.load(transformer_interval_json,
                                                          session=db.session)
        db.session.add(new_transformer_interval)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = TransformerIntervalSchema().dump(new_transformer_interval)

    return arw.to_json(result)
