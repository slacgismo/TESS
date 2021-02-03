from flask import Blueprint, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.utility import Utility, UtilitySchema

utility_api_bp = Blueprint('utility_api_bp', __name__)


@utility_api_bp.route('/utilities', methods=['GET'])
def get_utilities():
    '''
    Retrieves all utility objects
    '''
    arw = ApiResponseWrapper()

    utilities = Utility.query.all()
    utility_schema = UtilitySchema()
    results = utility_schema.dump(utilities, many=True)

    return arw.to_json(results)


@utility_api_bp.route('/utility/<int:utility_id>', methods=['GET'])
def show_utility_info(utility_id):
    '''
    Retrieves one utility object
    '''
    arw = ApiResponseWrapper()
    utility_schema = UtilitySchema()

    try:
        utility = Utility.query.filter_by(utility_id=utility_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = utility_schema.dump(utility)

    return arw.to_json(results)


@utility_api_bp.route('/utility/<int:utility_id>', methods=['PUT'])
def modify_utility(utility_id):
    '''
    Updates one utility object in database
    '''
    arw = ApiResponseWrapper()
    utility_schema = UtilitySchema()
    modified_utility = request.get_json()

    try:
        modified_utility = utility_schema.load(modified_utility,
                                               session=db.session)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = utility_schema.dump(modified_utility)

    return arw.to_json(results)


@utility_api_bp.route('/utility', methods=['POST'])
def add_utility():
    '''
    Adds new utility object to database
    '''
    arw = ApiResponseWrapper()
    utility_schema = UtilitySchema(exclude=['utility_id'])
    new_utility = request.get_json()

    try:
        new_utility = utility_schema.load(new_utility, session=db.session)
        db.session.add(new_utility)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = UtilitySchema().dump(new_utility)

    return arw.to_json(results)
