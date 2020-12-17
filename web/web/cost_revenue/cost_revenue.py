from flask import Blueprint, render_template, redirect
from flask_jwt_extended import (jwt_optional, get_jwt_identity)


cost_revenue_bp = Blueprint('cost_revenue_bp',
                            __name__,
                            template_folder='templates',
                            static_folder='static',
                            static_url_path='assets')


@cost_revenue_bp.route('/')
@jwt_optional
def index():
    has_tokens = get_jwt_identity()
    if has_tokens:
        return render_template('cost_revenue/index.html')
    else:
        return redirect('/?access_denied=true')
