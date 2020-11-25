from flask import request, jsonify, Blueprint
from werkzeug.security import generate_password_hash
from python_http_client.exceptions import (BadRequestsError, UnauthorizedError, MethodNotAllowedError,
                                           InternalServerError, NotFoundError)
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from flask_jwt_extended import (create_access_token, get_jwt_identity,
                                create_refresh_token, get_raw_jwt, get_jti, jwt_required)
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.login import Login, LoginSchema
from web.models.user import User, UserSchema
from web.redis import revoked_store
from web.config import JWT_ACCESS_EXPIRES, JWT_REFRESH_EXPIRES


login_api_bp = Blueprint('login_api_bp', __name__)


@login_api_bp.route('/login/<int:login_id>/reset_password', methods=['PATCH'])
@jwt_required
def reset_password(login_id):
    '''
    Resets password
    '''
    arw = ApiResponseWrapper()
    login_schema = LoginSchema()

    try:
        login = Login.query.filter_by(login_id=login_id).one()
        login_schema.load(request.get_json(), instance=login, partial=True, session=db.session)
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

    return arw.to_json(None, 200)


@login_api_bp.route('/login', methods=['POST'])
def create_login_info():
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
        revoked_store.set(access_jti, 'false', JWT_ACCESS_EXPIRES)

        refresh_token = create_refresh_token(identity=matching_login.login_id)
        refresh_jti = get_jti(encoded_token=refresh_token)
        revoked_store.set(refresh_jti, 'false', JWT_REFRESH_EXPIRES)

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
    Adds new user and login objects to database
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
        revoked_store.set(access_jti, 'false', JWT_ACCESS_EXPIRES)

        refresh_token = create_refresh_token(identity=new_login.login_id)
        refresh_jti = get_jti(encoded_token=refresh_token)
        revoked_store.set(refresh_jti, 'false', JWT_REFRESH_EXPIRES)

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

@login_api_bp.route('/logout', methods=['DELETE'])
@jwt_required
def logout():
    '''Revokes the current user's tokens to logout user'''

    arw = ApiResponseWrapper()

    try:
        access_token = get_raw_jwt()['jti']
        revoked_store.set(access_token, 'true', JWT_ACCESS_EXPIRES)

        refresh_token = request.cookies.get('refresh_token')
        refresh_jti = get_jti((refresh_token))
        revoked_store.set(refresh_jti, 'true', JWT_ACCESS_EXPIRES)

    except (BadRequestsError, UnauthorizedError, MethodNotAllowedError, InternalServerError, NotFoundError) as e:
        arw.add_errors(e.messages)

    if arw.has_errors():
        return arw.to_json(None, 400)

    return arw.to_json({'msg': 'Tokens revoked'}, 200)