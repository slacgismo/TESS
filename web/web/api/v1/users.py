from flask import Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.user import User, UserSchema

user_api_bp = Blueprint('user_api_bp', __name__)

@user_api_bp.route('/users', methods=['GET'])
def get_user_ids():
    """
    Retrieve all user objects
    """
    arw = ApiResponseWrapper()

    users = User.query.all()
    user_schema = UserSchema()
    results = user_schema.dump(users, many=True)
    
    return arw.to_json(results)


@user_api_bp.route('/<string:user_id>', methods=['GET'])
def show_user_info(user_id):
    pass


@user_api_bp.route('/<string:user_id>', methods=['PUT'])
def modify_user(user_id):
    pass


@user_api_bp.route('/user', methods=['POST'])
def add_user():
    pass