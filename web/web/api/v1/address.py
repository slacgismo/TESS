from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.address import Address, AddressSchema

address_api_bp = Blueprint('address_api_bp', __name__)


@address_api_bp.route('/addresses', methods=['GET'])
def get_addresses():
    '''
    Retrieves all address objects
    '''
    arw = ApiResponseWrapper()

    addresses = Address.query.all()
    address_schema = AddressSchema()
    results = address_schema.dump(addresses, many=True)

    return arw.to_json(results)


@address_api_bp.route('/address/<int:address_id>', methods=['GET'])
def show_address_info(address_id):
    '''
    Retrieves one address object
    '''

    arw = ApiResponseWrapper()
    address_schema = AddressSchema()

    try:
        address = Address.query.filter_by(address_id=address_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = address_schema.dump(address)

    return arw.to_json(results)


@address_api_bp.route('/address/<int:address_id>', methods=['PUT'])
def modify_address(address_id):
    '''
    Updates one address object in database
    '''
    arw = ApiResponseWrapper()
    address_schema = AddressSchema()
    modified_address = request.get_json()

    try:
        modified_address = address_schema.load(modified_address,
                                               session=db.session)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = address_schema.dump(modified_address)

    return arw.to_json(results)


@address_api_bp.route('/address', methods=['POST'])
def add_address():
    '''
    Adds new address object to database
    '''

    arw = ApiResponseWrapper()
    address_schema = AddressSchema(
        exclude=['address_id', 'created_at', 'updated_at'])
    new_address = request.get_json()

    try:
        new_address = address_schema.load(new_address, session=db.session)
        db.session.add(new_address)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = AddressSchema().dump(new_address)
    return arw.to_json(results)
