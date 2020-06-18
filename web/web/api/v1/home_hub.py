from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.home_hub import HomeHub, HomeHubSchema

home_hub_api_bp = Blueprint('home_hub_api_bp', __name__)

@home_hub_api_bp.route('/home_hubs', methods=['GET'])
def get_service_location_ids():
    '''
    Retrieves all home hub objects
    '''
    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in ServiceLocation.__table__.columns:
                arw.add_errors({field: 'Invalid Home Hub field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    home_hubs = HomeHub.query.all()
    home_hub_schema = HomeHubSchema(only=fields_to_filter_on)
    results = home_hub_schema.dump(home_hubs, many=True)

    return arw.to_json(results)

@home_hub_api_bp.route('/home_hub/<int:home_hub_id>', methods=['GET'])
def show_home_hub_info(home_hub_id):
    '''
    Retrieves one user object
    '''
    arw = ApiResponseWrapper()
    home_hub_schema = HomeHubSchema()

    try:
        home_hub = HomeHub.query.filter_by(home_hub_id=home_hub_id).one()

    except MultipleResultsFound:
        arw.add_errors(
            {home_hub_id: 'Multiple results found for the given home hub id.'})
        return arw.to_json(None, 400)

    except NoResultFound:
        arw.add_errors({home_hub_id: 'No results found for the given home hub id.'})
        return arw.to_json(None, 400)

    results = home_hub_schema.dump(home_hub)

    return arw.to_json(results)

@home_hub_api_bp.route('/home_hub/<int:home_hub_id>', methods=['PUT'])
def update_home_hub(home_hub_id):
    '''
    Updates home hub in database
    '''

    arw = ApiResponseWrapper()
    home_hub_schema = HomeHubSchema(exclude=['created_at'])
    modified_home_hub = request.get_json()

    try:
        HomeHub.query.filter_by(home_hub_id=home_hub_id).one()
        modified_home_hub = home_hub_schema.load(modified_home_hub, session=db.session)
        db.session.commit()

    except (MultipleResultsFound,NoResultFound):
        arw.add_errors('No result found or multiple results found')
    
    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Integrity error')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = home_hub_schema.dump(modified_home_hub)

    return arw.to_json(results)

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

    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)

    results = HomeHubSchema().dump(new_home_hub)
    return arw.to_json(results)
