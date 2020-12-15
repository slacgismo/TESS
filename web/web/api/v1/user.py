from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from datetime import datetime
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.user import User, UserSchema
from web.models.login import Login, LoginSchema

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

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = user_schema.dump(user)

    return arw.to_json(results)

@users_api_bp.route('/user/<int:user_id>', methods=['PUT'])
def modify_user(user_id):
    '''
    Updates one user object in database
    '''

    arw = ApiResponseWrapper()
    user_schema = UserSchema(exclude=[
        'updated_at', 'email_confirmed_at', 'created_at', 'roles',
        'postal_code'
    ])
    modified_user = request.get_json()

    try:
        User.query.filter_by(id=user_id).one()
        modified_user = user_schema.load(modified_user, session=db.session)
        db.session.commit()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = user_schema.dump(modified_user)

    return arw.to_json(results)


@users_api_bp.route('/user', methods=['POST'])
def add_user():
    '''
    Adds new user object to database
    '''
    arw = ApiResponseWrapper()
    user_schema = UserSchema(exclude=['id', 'created_at', 'updated_at'])
    new_user = request.get_json()

    try:
        new_user = user_schema.load(new_user, session=db.session)
        db.session.add(new_user)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = UserSchema().dump(new_user)

    return arw.to_json(results)


@users_api_bp.route('/update_user_settings', methods=['PATCH'])
@jwt_required
def updates_user_settings():
    '''
    Updates user and corresponding login in database
    '''

    arw = ApiResponseWrapper()
    user_schema = UserSchema()
    login_schema = LoginSchema()

    try:
        json = request.get_json()

        user = User.query.filter_by(id=json['user']['id']).one()
        updated_user = user_schema.load(json['user'], instance=user, partial=True, session=db.session)
        db.session.flush()

        if len(json['login']['password_hash']) == 0:
            del json['login']['password_hash']

        login = Login.query.filter_by(user_id=json['user']['id']).one()
        login_schema.load(json['login'], instance=login, partial=True, session=db.session)
        db.session.commit()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = user_schema.dump(updated_user)

    return arw.to_json(results)
