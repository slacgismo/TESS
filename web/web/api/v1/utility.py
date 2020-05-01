from web import app
from .response_wrapper import ApiResponseWrapper
from web.models.utility import Utility, UtilitySchema


@app.route('/api/v1/utilities', methods=['GET'])
def get_utilities():
    """
    Retrieve all utility objecgts
    """
    arw = ApiResponseWrapper()

    utilities = Utility.query.all()
    utility_schema = UtilitySchema()
    results = utility_schema.dump(utilities, many=True)
    
    return arw.to_json(results)