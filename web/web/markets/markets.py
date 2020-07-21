from flask import Blueprint, render_template

markets_bp = Blueprint('markets_bp',
                       __name__,
                       template_folder='templates',
                       static_folder='static',
                       static_url_path='assets')


@markets_bp.route('/')
def index():
    return render_template('markets/index.html')
