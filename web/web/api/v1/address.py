from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.address import Address, AddressSchema

address_api_bp = Blueprint('address_api_bp', __name__)

@address_api_bp.route('/address', methods=['POST'])
def add_address():
    '''
    Adds new address object to database
    '''

    arw = ApiResponseWrapper()
    address_schema = AddressSchema(exclude=['address_id', 'created_at', 'updated_at'])
    new_address = request.get_json()

    try:
        new_address = address_schema.load(new_address, session=db.session)
        db.session.add(new_address)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)

    except ValidationError as ve:
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = AddressSchema().dump(new_address)
    return arw.to_json(results)
