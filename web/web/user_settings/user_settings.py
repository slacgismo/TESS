from flask import Blueprint, render_template

user_settings_bp = Blueprint(
    'user_settings_bp', 
    __name__,
    template_folder='templates',
    static_folder='static', 
    static_url_path='assets'
)

@user_settings_bp.route('/')
def index():    
    return render_template('user_settings/index.html')