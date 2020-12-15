from flask import Blueprint, render_template
from flask_jwt_extended import jwt_required

user_settings_bp = Blueprint('user_settings_bp',
                             __name__,
                             template_folder='templates',
                             static_folder='static',
                             static_url_path='assets')


@user_settings_bp.route('/')
@jwt_required
def index():
    return render_template('user_settings/index.html')
