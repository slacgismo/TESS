# from datetime import timedelta
from flask import Blueprint, render_template, jsonify, redirect, request
from flask_jwt_extended import (jwt_required, create_access_token, get_current_user,
                                jwt_optional, get_jwt_identity, jwt_refresh_token_required, get_raw_jwt)
from web.redis import revoked_store
from web.config import JWT_ACCESS_EXPIRES, JWT_REFRESH_EXPIRES

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


@auth_bp.route('/auth/access_revoke', methods=['DELETE'])
@jwt_required
def logout():
    '''Revokes the current user's access token'''
    jti = get_raw_jwt()['jti']
    revoked_store.set(jti, 'true', JWT_ACCESS_EXPIRES)
    return jsonify({'msg': 'Access token revoked'}), 200


@auth_bp.route('/auth/refresh_revoke', methods=['DELETE'])
@jwt_refresh_token_required
def logout2():
    '''Revokes the current user's refresh token'''
    jti = get_raw_jwt()['jti']
    revoked_store.set(jti, 'true', JWT_REFRESH_EXPIRES)
    return jsonify({'msg': 'Refresh token revoked'}), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_refresh_token_required
def refresh():
    '''Regenerates access token, with refresh token'''
    current_user = get_jwt_identity()
    access_token = {
        'access_token': create_access_token(identity=current_user)
    }
    return jsonify(access_token), 200
