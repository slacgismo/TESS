from flask import Blueprint, render_template, redirect
from flask_jwt_extended import (jwt_optional, get_jwt_identity)

auth_bp = Blueprint('auth_bp',
                    __name__,
                    template_folder='templates',
                    static_folder='static',
                    static_url_path='assets')


@auth_bp.route('/')
@auth_bp.route('/auth', strict_slashes=False)
@jwt_optional
def index():
    has_tokens = get_jwt_identity()
    if has_tokens:
        return redirect('power/capacity')
    else:
        return render_template('auth/login.html')
