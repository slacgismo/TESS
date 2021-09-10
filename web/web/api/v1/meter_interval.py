import os
import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper

from web.models.pv import Pv, PvSchema
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
    meter_id = request.args.get('meter_id', None)

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

        if meter_id:
            meter_id = int(meter_id)
            mi = mi.filter(MeterInterval.meter_id == meter_id)

    except parser.ParserError as pe:
        arw.add_errors(
            'Could not parse the date time value. Please provide a valid format.'
        )
        return arw.to_json(None, 400)

    except ValueError as ve:
        arw.add_errors(
            'Could not parse the meter id. It should be an integer.')
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


@meter_interval_api_bp.route('/meter_interval_latest/<int:meter_id>',
                             methods=['GET'])
def retrieve_latest_meter_interval_info(meter_id):
    '''
    Retrieves the last meter_interval based on a given meter id
    '''

    arw = ApiResponseWrapper()
    meter_interval_schema = MeterIntervalSchema()

    try:
        meter_interval = MeterInterval.query.filter_by(
            meter_id=meter_id).order_by(-MeterInterval.meter_interval_id).first()

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
    print(results)
    # have to export AWS envvar as True
    # within an if statement for ease of simulation testing
    if (os.getenv('AWS')=="True"):

        # get homehub id from the PV table using meter_id
        pv_schema = PvSchema()
        pv = Pv.query.filter_by(meter_id=results["meter_id"]).one()
        homehub_id = pv.home_hub_id
        # TODO: implement battery and ev into the backend and fix hardcoded data below
        payload = [
                    {"resource": "solar", "payload": {"mode_dispatch": results['mode_dispatch'], "qmtp" : results["qmtp"]}},
                    {"resource": "battery", "payload": {"mode_dispatch": None, "qmtp" : None}},
                    {"resource": "ev", "payload": {"mode_dispatch": None, "qmtp" : None}}
                  ]

        # publishes data to TessEvents topic
        from web.iot_core.iot_pubsub import publish
        publish(payload=payload, device_id=homehub_id)
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
