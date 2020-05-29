from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.group import Group, GroupSchema

group_api_bp = Blueprint('group_api_bp', __name__)

@group_api_bp.route('/groups', methods=['GET'])
def get_user_ids():
    '''
    Retrieve all user objects
    '''
    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Group.__table__.columns:
                arw.add_errors({field: 'Invalid Group field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    groups = Group.query.all()
    group_schema = GroupSchema(only=fields_to_filter_on)
    results = group_schema.dump(groups, many=True)
    
    return arw.to_json(results)


@group_api_bp.route('/group/<string:group_id>', methods=['GET'])
def show_user_info(user_id):
    '''
    Retrieve one user object
    '''
    arw = ApiResponseWrapper()
    group_schema = GroupSchema()

    try:  
        service_location = Group.query.filter_by(group_id=group_id).one()
    
    except MultipleResultsFound:
        arw.add_errors({group_id: 'Multiple results found for the given service location id.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({group_id: 'No results found for the given service location id.'})
        return arw.to_json()

    results = group_schema.dump(group)

    return arw.to_json(results)


@group_api_bp.route('servicelocation/<string:group_id>', methods=['PUT'])
def modify_user(user_id):
    '''
    Update one user object in database
    '''
    arw = ApiResponseWrapper()
    group_schema = GroupSchema(exclude=['email_confirmed_at', 'created_at', 'address'])
    modified_group = request.get_json()

    try:
        Group.query.filter_by(group_id=group_id).one()
        modified_group = group_schema.load(modified_group, session=db.session)
        db.session.commit()

    except MultipleResultsFound:
        arw.add_errors({group_id: 'Multiple results found for the given group id.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({group_id: 'No results found for the given group id.'})
        return arw.to_json()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)
    
    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = group_schema.dump(modified_group)

    return arw.to_json(results)


@group_api_bp.route('/servicelocation', methods=['POST'])
def add_user():
    '''
    Add new user object to database
    '''
    arw = ApiResponseWrapper()
    group_schema = GroupSchema()
    new_group = request.get_json()
            
    try:
        does_group_exist = Group.query.filter_by(id=new_group['group_id']).count() > 0

        if does_group_exist:
            raise IntegrityError('Group already exists', None, None)
        
        new_group= group_schema.load(new_group, session=db.session)
        db.session.add(new_group)
        db.session.commit()

    except IntegrityError as ie:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)
    
    except ValidationError as ve:
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)
    
    results = GroupSchema().dump(new_group)
    return arw.to_json(results)