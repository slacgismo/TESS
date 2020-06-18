from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.home_hub import HomeHub, HomeHubSchema

home_hub_api_bp = Blueprint('home_hub_api_bp', __name__)

@home_hub_api_bp.route('/home_hub', methods=['POST'])
def add_home_hub():
    '''
    Adds new home hub object to database
    '''
    
    arw = ApiResponseWrapper()
    home_hub_schema = HomeHubSchema(
        exclude=['home_hub_id', 'created_at', 'updated_at'])
    new_home_hub = request.get_json()

    try:
        new_home_hub = home_hub_schema.load(new_home_hub, session=db.session)
        db.session.add(new_home_hub)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)

    except ValidationError as ve:
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = HomeHubSchema().dump(new_home_hub)
    return arw.to_json(results)
