from flask import Blueprint, render_template, redirect
from flask_jwt_extended import (jwt_optional, get_jwt_identity)

residential_sd_bp = Blueprint('residential_sd_bp',
                        __name__,
                        template_folder='templates',
                        static_folder='static',
                        static_url_path='assets')


@residential_sd_bp.route('/')
@residential_sd_bp.route('/residential_sd')
@jwt_optional
def index():
    has_tokens = get_jwt_identity()
    if has_tokens:
        return render_template('residential_sd/index.html')
    else:
        return redirect('/?access_denied=true')
