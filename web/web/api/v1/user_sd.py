from flask import Blueprint, request
from .response_wrapper import ApiResponseWrapper

user_sd_api_bp = Blueprint('user_sd_api_bp', __name__)


@user_sd_api_bp.route('/user_sd/system_load/', methods=['GET'])
def get_power_system_load():
    arw = ApiResponseWrapper()
    return True
