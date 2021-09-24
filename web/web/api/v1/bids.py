from web.database import db
import dateutil.parser as parser
from flask import request, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .response_wrapper import ApiResponseWrapper
from web.models.hce_bids import HceBids, HceBidsSchema
from web.models.meter_interval import MeterInterval, MeterIntervalSchema

bids_api_bp = Blueprint('bids_api_bp', __name__)


@bids_api_bp.route('/bids', methods=['GET'])
def get_bids():
    '''
    Get the supply or demand bids
    '''
    arw = ApiResponseWrapper()
    start_time = request.args.get('start_time', None)
    is_supply = request.args.get('is_supply', '')

    try:
        results = []
        if start_time:
            start_time = parser.parse(start_time)

        hb_schema = HceBidsSchema()
        hb = HceBids.query.filter()

        if is_supply.lower() == 'false':
            hb = hb.filter(HceBids.is_supply.is_(False))
            if start_time:
                hb = hb.filter(HceBids.start_time == start_time)
            results.append(hb_schema.dump(hb, many=True))

        elif is_supply.lower() == 'true':
            # get the meter_intervals as well
            hb = hb.filter(HceBids.is_supply.is_(True))
            mi_schema = MeterIntervalSchema()
            mi = MeterInterval.query.filter()
            if start_time:
                hb = hb.filter(HceBids.start_time == start_time)
                mi = mi.filter(MeterInterval.start_time == start_time)
            results.append(hb_schema.dump(hb, many=True))
            results.append(mi_schema.dump(mi, many=True))

        else:
            arw.add_errors('is_supply query param is required')

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


@bids_api_bp.route('/bids', methods=['POST'])
def add_bid():
    '''
    adds new HCEBids to database
    '''

    arw = ApiResponseWrapper()
    hb_schema = HceBidsSchema(
            exclude=['bid_id', 'created_at', 'updated_at']
    )
    new_bid = request.get_json()

    try:
        new_bid = hb_schema.load(new_bid, session=db.session)
        db.session.add(new_bid)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = HceBidsSchema().dump(new_bid)
    return arw.to_json(results)
