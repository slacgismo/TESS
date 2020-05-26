from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.user import User, UserSchema
from web.models.address import Address
from web.models.role import Role, RoleType
from web.models.group import Group
from web.models.utility import Utility
from datetime import datetime

users_api_bp = Blueprint('users_api_bp', __name__)

@users_api_bp.route('/users', methods=['GET'])
def get_user_ids():
    '''
    Retrieve all user objects
    '''
    arw = ApiResponseWrapper()

    users = User.query.all()
    user_schema = UserSchema()
    results = user_schema.dump(users, many=True)
    
    return arw.to_json(results)


@users_api_bp.route('/user/<string:user_id>', methods=['GET'])
def show_user_info(user_id):
    '''
    Retrieve one user object
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema()

    try:  
        user = User.query.filter_by(user_id=user_id).one()
    
    except MultipleResultsFound:
        arw.add_errors({user_id: 'Multiple results found for the given user id.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({user_id: 'No results found for the given user id.'})
        return arw.to_json()

    results = user_schema.dump(user)

    return arw.to_json(results)


@users_api_bp.route('user/<string:user_id>', methods=['PUT'])
def modify_user(user_id):
    '''
    Update one user object in database
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema(exclude=['email_confirmed_at', 'created_at'])
    modified_user = request.get_json()

    try:
        User.query.filter_by(user_id=user_id).one()
        modified_user = user_schema.load(modified_user, session=db.session)
        db.session.commit()

    except MultipleResultsFound:
        arw.add_errors({user_id: 'Multiple results found for the given user id.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({user_id: 'No results found for the given user id.'})
        return arw.to_json()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)
    
    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = user_schema.dump(modified_user)

    return arw.to_json(results)


@users_api_bp.route('/user', methods=['POST'])
def add_user():
    '''
    Add new user object to database
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema()
    new_user = request.get_json()
            
    try:
        does_user_exist = User.query.filter_by(email=new_user['email']).count() > 0

        if does_user_exist:
            raise IntegrityError('Email already in use', None, None)
        
        new_user = user_schema.load(new_user, session=db.session)
        db.session.add(new_user)
        db.session.commit()

    except IntegrityError as ie:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)
    
    except ValidationError as ve:
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)
    
    results = UserSchema().dump(new_user)
    return arw.to_json(results)