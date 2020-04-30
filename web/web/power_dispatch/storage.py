from flask import Blueprint, render_template

storage_bp = Blueprint(
    'storage_bp', 
    __name__,
    template_folder='templates',
    static_folder='static', 
    static_url_path='assets'
)

@storage_bp.route('/')
def index():    
    return render_template('storage/index.html')