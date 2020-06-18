from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from datetime import datetime
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.user import User, UserSchema

users_api_bp = Blueprint('users_api_bp', __name__)


@users_api_bp.route('/users', methods=['GET'])
def get_user_ids():
    '''
    Retrieves all user objects
    '''
    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in User.__table__.columns:
                arw.add_errors({field: 'Invalid User field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    users = User.query.all()
    user_schema = UserSchema(exclude=['address_id'], only=fields_to_filter_on)
    results = user_schema.dump(users, many=True)

    return arw.to_json(results)


@users_api_bp.route('/user/<int:user_id>', methods=['GET'])
def show_user_info(user_id):
    '''
    Retrieves one user object
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema(exclude=['address_id'])

    try:
        user = User.query.filter_by(id=user_id).one()

    except MultipleResultsFound:
        arw.add_errors(
            {user_id: 'Multiple results found for the given user id.'})
        return arw.to_json(None, 400)

    except NoResultFound:
        arw.add_errors({user_id: 'No results found for the given user id.'})
        return arw.to_json(None, 400)

    results = user_schema.dump(user)

    return arw.to_json(results)


@users_api_bp.route('user/<int:user_id>', methods=['PUT'])
def modify_user(user_id):
    '''
    Updates one user object in database
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema(
        exclude=['email_confirmed_at', 'created_at'])
    modified_user = request.get_json()

    try:
        User.query.filter_by(id=user_id).one()
        modified_user = user_schema.load(modified_user, session=db.session)
        db.session.commit()

    except MultipleResultsFound:
        arw.add_errors(
            {user_id: 'Multiple results found for the given user id.'})
        return arw.to_json(None, 400)

    except NoResultFound:
        arw.add_errors({user_id: 'No results found for the given user id.'})
        return arw.to_json(None, 400)

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
    Adds new user object to database
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema(exclude=['user_id', 'created_at', 'updated_at'])
    new_user = request.get_json()

    try:
        new_user = user_schema.load(new_user, session=db.session)
        db.session.add(new_user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)

    except ValidationError as ve:
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = UserSchema().dump(new_user)

    return arw.to_json(results)
