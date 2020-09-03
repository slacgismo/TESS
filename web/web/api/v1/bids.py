from web.database import db
from flask import request, Blueprint
from marshmallow import ValidationError
from web.models.hce_bids import HceBids
from sqlalchemy.exc import IntegrityError
from .response_wrapper import ApiResponseWrapper
from web.models.meter_interval import MeterInterval
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

bids_api_bp = Blueprint('bids_api_bp', __name__)


@bids_api_bp.route('/bids/', methods=['GET'])
def get_bids():
    '''
    
    '''
    arw = ApiResponseWrapper()

    try:
        results = []

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    return arw.to_json(results)
