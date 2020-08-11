import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.meter_interval import MeterInterval, MeterIntervalSchema

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

meter_interval_api_bp = Blueprint('meter_interval_api_bp', __name__)


@meter_interval_api_bp.route('/meter_intervals', methods=['GET'])
def get_meter_intervals():
    '''
    Returns meter intervals
    '''

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')
    start_time = request.args.get('start_time', None)
    end_time = request.args.get('end_time', None)

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in MeterInterval.__table__.columns:
                arw.add_errors({field: 'Invalid Meter Interval field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    meter_interval_schema = MeterIntervalSchema(only=fields_to_filter_on)

    mi = MeterInterval.query.filter()

    try:
        if start_time:
            start_time = parser.parse(start_time)
            mi = mi.filter(MeterInterval.start_time >= start_time)
        if end_time:
            end_time = parser.parse(end_time)
            mi = mi.filter(MeterInterval.end_time <= end_time)
    except parser.ParserError as pe:
        arw.add_errors(
            'Could not parse the date time value. Please provide a valid format.'
        )
        return arw.to_json(None, 400)

    results = meter_interval_schema.dump(mi, many=True)

    return arw.to_json(results)


@meter_interval_api_bp.route('/meter_interval/<int:meter_interval_id>',
                             methods=['GET'])
def retrieve_meter_interval_info(meter_interval_id):
    '''
    Retrieves one meter interval as json object
    '''

    arw = ApiResponseWrapper()
    meter_interval_schema = MeterIntervalSchema()

    try:
        meter_interval = MeterInterval.query.filter_by(
            meter_interval_id=meter_interval_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = meter_interval_schema.dump(meter_interval)

    return arw.to_json(results)


@meter_interval_api_bp.route('/meter_interval/<int:meter_interval_id>',
                             methods=['PUT'])
def update_meter_interval(meter_interval_id):
    '''
    Updates meter interval in database
    '''

    arw = ApiResponseWrapper()
    meter_interval_schema = MeterIntervalSchema()
    modified_meter_interval = request.get_json()

    try:
        MeterInterval.query.filter_by(
            meter_interval_id=meter_interval_id).one()
        modified_meter_interval = meter_interval_schema.load(
            modified_meter_interval, session=db.session)
        db.session.commit()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = meter_interval_schema.dump(modified_meter_interval)

    return arw.to_json(results)


@meter_interval_api_bp.route('/meter_interval', methods=['POST'])
def add_meter_interval():
    '''
    Adds new meter interval to database
    '''

    arw = ApiResponseWrapper()
    meter_interval_schema = MeterIntervalSchema(exclude=['meter_interval_id'])
    meter_interval_json = request.get_json()

    try:
        new_meter_interval = meter_interval_schema.load(meter_interval_json,
                                                        session=db.session)
        db.session.add(new_meter_interval)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = MeterIntervalSchema().dump(new_meter_interval)

    return arw.to_json(result)
