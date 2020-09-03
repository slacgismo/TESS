from web.database import db
import dateutil.parser as parser
from flask import request, Blueprint
from marshmallow import ValidationError
from web.models.hce_bids import HceBids
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .response_wrapper import ApiResponseWrapper
from web.models.meter_interval import MeterInterval

bids_api_bp = Blueprint('bids_api_bp', __name__)


@bids_api_bp.route('/bids/', methods=['GET'])
def get_bids():
    '''
    Get the supply or demand bids 
    '''
    arw = ApiResponseWrapper()
    start_time = request.args.get('start_time', None)
    is_supply = request.args.get('is_supply', None)

    try:
        results = []
        if start_time:
            start_time = parser.parse(start_time)

        if is_supply.lower() == 'false':
            # get the hce bids only

        if is_supply.lower() == 'true':
            # get the meter interval and hce bids

        # otherwise, just get both

    except parser.ParserError as pe:
        arw.add_errors(
            'Could not parse the date time value. Please provide a valid format.'
        )
        return arw.to_json(None, 400)

    except NoResultFound:
        arw.add_errors('No result found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    return arw.to_json(results)
