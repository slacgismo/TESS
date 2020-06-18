import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.market_interval import MarketInterval, MarketIntervalSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


market_interval_api_bp = Blueprint('market_interval_api_bp', __name__)


@market_interval_api_bp.route('/market_interval/<int:market_interval_id>', methods=['GET'])
def show_market_interval_info(market_interval_id):
    '''
    Returns market interval information as json object
    '''

    arw = ApiResponseWrapper()
    meter_schema = MarketIntervalSchema()

    try:  
        market_interval = MarketInterval.query.filter_by(market_interval_id=market_interval_id).one()
    
    except MultipleResultsFound:
        arw.add_errors({market_interval_id: 'Multiple results found for the given market interval.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({market_interval_id: 'No results found for the given market interval.'})
        return arw.to_json()

    results = meter_schema.dump(market_interval)
    return arw.to_json(results)

@market_interval_api_bp.route('/market_interval/<int:market_interval_id>', methods=['PUT'])
def update_market_interval(market_interval_id):
    '''
    Updates market interval in database
    '''

    arw = ApiResponseWrapper()
    market_interval_schema = MarketIntervalSchema()
    modified_market_interval = request.get_json()

    try:
        MarketInterval.query.filter_by(market_interval_id=market_interval_id).one()
        modified_market_interval = market_interval_schema.load(modified_market_interval, session=db.session)
        db.session.commit()

    except (MultipleResultsFound,NoResultFound):
        arw.add_errors('No result found or multiple results found')
    
    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Integrity error')
    
    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = market_interval_schema.dump(modified_market_interval)

    return arw.to_json(results)


@market_interval_api_bp.route('/market_interval', methods=['POST'])
def add_market_interval():
    '''
    Adds new market interval to database
    '''

    arw = ApiResponseWrapper()
    market_interval_schema = MarketIntervalSchema(exclude=['market_interval_id'])
    market_interval_json = request.get_json()
            
    try:
        new_market_interval = market_interval_schema.load(market_interval_json, session=db.session)
        db.session.add(new_market_interval)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors({'market_interval_id': 'The given market interval already exists.'})
        return arw.to_json(None, 400)
    
    except ValidationError as e:
        arw.add_errors(e.messages)
        return arw.to_json(None, 400)
    
    result = MarketIntervalSchema().dump(new_market_interval)
    return arw.to_json(result)
