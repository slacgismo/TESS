from flask import request, jsonify, Blueprint
from datetime import timedelta
from werkzeug.security import generate_password_hash
from python_http_client.exceptions import BadRequestsError
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                create_refresh_token, jwt_required, jwt_optional, get_raw_jwt, get_current_user, get_jti)
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.login import Login, LoginSchema
from web.models.user import User, UserSchema
from web.redis import revoked_store


login_api_bp = Blueprint('login_api_bp', __name__)


@login_api_bp.route('/login/<int:login_id>', methods=['GET'])
def show_login_info(login_id):
    '''
    Retrieves one login object
    '''
    arw = ApiResponseWrapper()
    login_schema = LoginSchema(exclude=['password_hash'])

    try:
        login = Login.query.filter_by(login_id=login_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = login_schema.dump(login)

    return arw.to_json(results)


@login_api_bp.route('/login/<int:login_id>', methods=['PUT'])
def modify_login(login_id):
    '''
    Updates one login object in database
    '''

    arw = ApiResponseWrapper()
    login_schema = LoginSchema(exclude=[
        'updated_at', 'created_at'
    ])
    modified_login = request.get_json()

    try:
        Login.query.filter_by(login_id=login_id).one()
        modified_login = login_schema.load(modified_login, session=db.session)
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

    results = login_schema.dump(modified_login)

    return arw.to_json(results)


@login_api_bp.route('/login', methods=['POST'])
def check_login_info():
    '''
    Login user
    '''
    arw = ApiResponseWrapper()
    login_data = request.get_json()

    try:
        matching_login = Login.query.filter_by(
            username=login_data['username']).one()
        matching_login.check_password(login_data['password_hash'])

        access_token = create_access_token(identity=matching_login.login_id)
        access_jti = get_jti(encoded_token=access_token)
        revoked_store.set(access_jti, 'false', timedelta(minutes=15) * 1.2)

        refresh_token = create_refresh_token(identity=matching_login.login_id)
        refresh_jti = get_jti(encoded_token=refresh_token)
        revoked_store.set(refresh_jti, 'false',  timedelta(days=30) * 1.2)

        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    except ValueError:
        arw.add_errors('Value error')

    except BadRequestsError:
        arw.add_errors('Bad requests error')

    if arw.has_errors():
        return arw.to_json(None, 400)

    return arw.to_json(tokens, 201)


@login_api_bp.route('/sign_up', methods=['POST'])
def process_sign_up():
    '''
    Adds new user and login object to database
    '''
    arw = ApiResponseWrapper()
    sign_up_data = request.get_json()

    user_schema = UserSchema(exclude=['id', 'created_at', 'updated_at'])
    login_schema = LoginSchema(
        exclude=['login_id', 'created_at', 'updated_at'])

    try:
        new_user = user_schema.load(sign_up_data['user'], session=db.session)
        db.session.add(new_user)
        db.session.flush()

        sign_up_data['login']['user_id'] = new_user.id
        new_login = login_schema.load(
            sign_up_data['login'], session=db.session)
        db.session.add(new_login)
        db.session.commit()

        access_token = create_access_token(identity=new_login.login_id)
        access_jti = get_jti(encoded_token=access_token)
        revoked_store.set(access_jti, 'false', timedelta(minutes=15) * 1.2)

        refresh_token = create_refresh_token(identity=new_login.login_id)
        refresh_jti = get_jti(encoded_token=refresh_token)
        revoked_store.set(refresh_jti, 'false',  timedelta(days=30) * 1.2)

        tokens = {
            'access_token': access_token,
            'refresh_token': refresh_token
        }

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    return arw.to_json(tokens, 201)


#  COMMENT OUT FOR TESTING FLASK-JWT-EXT


# @login_api_bp.route('/check')
# @jwt_optional
# def check_login():
#     arw = ApiResponseWrapper()
#     current_user = get_raw_jwt()['jti']
#     user_has_tokens = get_jwt_identity()
#     return arw.to_json({"user": current_user, "tokens": user_has_tokens})
