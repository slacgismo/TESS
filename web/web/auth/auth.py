from flask import Blueprint, render_template

auth_bp = Blueprint(
    'auth_bp', 
    __name__,
    template_folder='templates',
    static_folder='static', 
    static_url_path='assets'
)

@auth_bp.route('/')
def index():
    return render_template('auth/login.html')
