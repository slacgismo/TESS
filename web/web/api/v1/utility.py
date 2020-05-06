from web import app, db
from flask import request
from .response_wrapper import ApiResponseWrapper
from web.models.utility import Utility, UtilitySchema


@app.route('/api/v1/utilities', methods=['GET'])
def get_utilities():
    """
    Retrieve all utility objects
    """
    arw = ApiResponseWrapper()

    utilities = Utility.query.all()
    utility_schema = UtilitySchema()
    results = utility_schema.dump(utilities, many=True)
    
    return arw.to_json(results)


@app.route('/api/v1/utilities', methods=['POST'])
def post_utilities():
    """
    Retrieve all utility objects
    """
    arw = ApiResponseWrapper()
    serialized_util = request.get_json()
    
    utility_schema = UtilitySchema()
    try:
        util = utility_schema.load(serialized_util, session=db.session)
        db.session.add(util)
        db.session.commit()
    except Exception as e:
        print(e)
        
    return arw.to_json()
