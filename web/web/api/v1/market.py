import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.market import Market, MarketSchema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


market_api_bp = Blueprint('market_api_bp', __name__)


@market_api_bp.route('/market/<int:market_id>', methods=['GET'])
def show_market_info(market_id):
    '''
    Returns market information as json object
    '''
    arw = ApiResponseWrapper()
    market_schema = MarketSchema()

    try:  
        market = Market.query.filter_by(market_id=market_id).one()
    
    except MultipleResultsFound:
        arw.add_errors({market_id: 'Multiple results found for the given market.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({market_id: 'No results found for the given market.'})
        return arw.to_json()

    results = market_schema.dump(market)
    return arw.to_json(results)


@market_api_bp.route('/market/<int:market_id>', methods=['PUT'])
def update_market(market_id):
    '''Updates market in database'''

    arw = ApiResponseWrapper()
    market_schema = MarketSchema(exclude=['created_at'])
    modified_market = request.get_json()

    try:
        Market.query.filter_by(market_id=market_id).one()
        modified_market = market_schema.load(modified_market, session=db.session)
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

    results = market_schema.dump(modified_market)

    return arw.to_json(results)


@market_api_bp.route('/market', methods=['POST'])
def add_market():
    '''Add new market to database'''
    
    arw = ApiResponseWrapper()
    market_schema = MarketSchema(exclude=['market_id', 'created_at', 'updated_at'])
    market_json = request.get_json()
            
    try:
        new_market = market_schema.load(market_json, session=db.session)
        db.session.add(new_market)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors({'market_id': 'The given market already exists.'})
        return arw.to_json(None, 400)
    
    except ValidationError as e:
        arw.add_errors(e.messages)
        return arw.to_json(None, 400)
    
    result = MarketSchema().dump(new_market)
    return arw.to_json(result)
