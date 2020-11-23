from flask import Blueprint, render_template


cost_revenue_bp = Blueprint('cost_revenue_bp',
                            __name__,
                            template_folder='templates',
                            static_folder='static',
                            static_url_path='assets')


@cost_revenue_bp.route('/')
def index():
    return render_template('cost_revenue/index.html')
