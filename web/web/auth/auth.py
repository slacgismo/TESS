from flask import Blueprint, render_template, jsonify, redirect, request
from flask_jwt_extended import (jwt_required, create_access_token, get_current_user,
                                jwt_optional, get_jti, get_jwt_identity, jwt_refresh_token_required, get_raw_jwt)
from python_http_client.exceptions import (BadRequestsError, UnauthorizedError, MethodNotAllowedError,
                                           InternalServerError, NotFoundError)
from web.redis import revoked_store
from web.config import JWT_ACCESS_EXPIRES, JWT_REFRESH_EXPIRES
from web.api.v1.response_wrapper import ApiResponseWrapper

auth_bp = Blueprint('auth_bp',
                    __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='assets')


@auth_bp.route('/')
@auth_bp.route('/auth', strict_slashes=False)
@jwt_optional
def index():
    access_token = request.cookies.get('access_token')
    if access_token:
        return redirect('power/capacity')
    else:
        return render_template('auth/login.html')


# see this repo for JWT redis blacklist setup:
# https://github.com/vimalloc/flask-jwt-extended/blob/master/examples/redis_blacklist.py

@auth_bp.route('/auth/revoke', methods=['DELETE'])
@jwt_required
def logout():
    '''Revokes the current user's tokens'''

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


@auth_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    '''Regenerates access token, with refresh token'''
    current_user = get_jwt_identity()
    access_token = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(access_token), 200
