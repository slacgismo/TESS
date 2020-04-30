from flask import Blueprint, render_template

alerts_bp = Blueprint(
    'alerts_bp', 
    __name__,
    template_folder='templates',
    static_folder='static', 
    static_url_path='assets'
)

@alerts_bp.route('/')
def index():    
    return render_template('alerts/index.html')
