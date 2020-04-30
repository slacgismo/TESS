from flask import Blueprint, render_template

notifications_bp = Blueprint(
    'notifications_bp', 
    __name__,
    template_folder='templates',
    static_folder='static', 
    static_url_path='assets'
)

@notifications_bp.route('/')
def index():    
    return render_template('notifications/index.html')
