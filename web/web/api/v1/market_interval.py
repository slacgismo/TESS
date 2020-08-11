import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.market_interval import MarketInterval, MarketIntervalSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

market_interval_api_bp = Blueprint('market_interval_api_bp', __name__)


@market_interval_api_bp.route('/market_intervals', methods=['GET'])
def get_market_intervals():
    '''
    Returns market intervals
    '''

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in MarketInterval.__table__.columns:
                arw.add_errors({field: 'Invalid Market Interval field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    market_interval_schema = MarketIntervalSchema(only=fields_to_filter_on)

    mi = MarketInterval.query.all()

    results = market_interval_schema.dump(mi, many=True)

    return arw.to_json(results)


@market_interval_api_bp.route('/market_interval/<int:market_interval_id>',
                              methods=['GET'])
def show_market_interval_info(market_interval_id):
    '''
    Returns market interval information as json object
    '''

    arw = ApiResponseWrapper()
    meter_schema = MarketIntervalSchema()

    try:
        market_interval = MarketInterval.query.filter_by(
            market_interval_id=market_interval_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = meter_schema.dump(market_interval)

    return arw.to_json(results)


@market_interval_api_bp.route('/market_interval/<int:market_interval_id>',
                              methods=['PUT'])
def update_market_interval(market_interval_id):
    '''
    Updates market interval in database
    '''

    arw = ApiResponseWrapper()
    market_interval_schema = MarketIntervalSchema()
    modified_market_interval = request.get_json()

    try:
        MarketInterval.query.filter_by(
            market_interval_id=market_interval_id).one()
        modified_market_interval = market_interval_schema.load(
            modified_market_interval, session=db.session)
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

    results = market_interval_schema.dump(modified_market_interval)

    return arw.to_json(results)


@market_interval_api_bp.route('/market_interval', methods=['POST'])
def add_market_interval():
    '''
    Adds new market interval to database
    '''

    arw = ApiResponseWrapper()
    market_interval_schema = MarketIntervalSchema(
        exclude=['market_interval_id'])
    market_interval_json = request.get_json()

    try:
        new_market_interval = market_interval_schema.load(market_interval_json,
                                                          session=db.session)
        db.session.add(new_market_interval)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = MarketIntervalSchema().dump(new_market_interval)

    return arw.to_json(result)
