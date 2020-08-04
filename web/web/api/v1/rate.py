from flask import request, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.rate import Rate, RateSchema

rate_api_bp = Blueprint('rate_api_bp', __name__)


@rate_api_bp.route('/rates', methods=['GET'])
def get_rates():
    '''
    Retrieves all rate objects
    '''
    arw = ApiResponseWrapper()

    rates = Rate.query.all()
    rate_schema = RateSchema()
    results = rate_schema.dump(rates, many=True)

    return arw.to_json(results)


@rate_api_bp.route('/rate/<int:rate_id>', methods=['GET'])
def show_rate_info(rate_id):
    '''
    Retrieves one rate object
    '''
    arw = ApiResponseWrapper()
    rate_schema = RateSchema()

    try:
        rate = Rate.query.filter_by(rate_id=rate_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = rate_schema.dump(rate)

    return arw.to_json(results)


@rate_api_bp.route('/rate/<int:rate_id>', methods=['PUT'])
def modify_rate(rate_id):
    '''
    Updates one rate object in database
    '''
    arw = ApiResponseWrapper()
    rate_schema = RateSchema(exclude=['rate_id'])
    modified_rate = request.get_json()

    try:
        modified_rate = rate_schema.load(modified_rate, session=db.session)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = rate_schema.dump(modified_rate, many=True)

    return arw.to_json(results)


@rate_api_bp.route('/rate', methods=['POST'])
def add_rates():
    '''
    Adds new rate object to database
    '''

    arw = ApiResponseWrapper()
    rate_schema = RateSchema(exclude=['rate_id'])
    new_rate = request.get_json()

    try:
        new_rate = rate_schema.load(new_rate, session=db.session)
        db.session.add(new_rate)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = RateSchema().dump(new_rate)
    return arw.to_json(results)
