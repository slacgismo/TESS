from flask import Blueprint, render_template

capacity_bp = Blueprint(
    'capacity_bp', 
    __name__,
    template_folder='templates',
    static_folder='static', 
    static_url_path='assets'
)

@capacity_bp.route('/')
def index():    
    return render_template('capacity/index.html')
