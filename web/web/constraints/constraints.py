from flask import Blueprint, render_template


constraints_bp = Blueprint('constraints_bp',
                           __name__,
                           template_folder='templates',
                           static_folder='static',
                           static_url_path='assets')


@constraints_bp.route('/')
def index():
    # return render_template('constraints/index.html')
    return render_template('404.html'), 404
