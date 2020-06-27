from flask import Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.utility import Utility, UtilitySchema

utility_api_bp = Blueprint('utility_api_bp', __name__)


@utility_api_bp.route('/utilities', methods=['GET'])
def get_utilities():
    '''
    Retrieves all utility objects
    '''
    arw = ApiResponseWrapper()

    utilities = Utility.query.all()
    utility_schema = UtilitySchema()
    results = utility_schema.dump(utilities, many=True)

    return arw.to_json(results)
