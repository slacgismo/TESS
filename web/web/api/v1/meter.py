import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from web.api.v1.schema.meter import schema_data
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.meter import Meter, MeterSchema, MeterType
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

meter_api_bp = Blueprint('meter_api_bp', __name__)


@meter_api_bp.route('/meters', methods=['GET'])
def get_meter_ids():
    '''
    Returns all meter objects
    TODO: support query string filtering on props like is_active/is_archived
    TODO: decorator or Mixin for fields_to_filter_on!!!
    '''

    arw = ApiResponseWrapper()

    # get the list fields we want on the response
    fields_to_filter_on = request.args.getlist('fields')

    # validate that they exist
    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Meter.__table__.columns:
                arw.add_errors({field: 'Invalid Meter field'})
                return arw.to_json(None, 400)
    else:
        # make sure we get everything if no fields are given
        fields_to_filter_on = None

    meter_schema = MeterSchema(only=fields_to_filter_on)
    meters = Meter.query.all()
    results = meter_schema.dump(meters, many=True)

    return arw.to_json(results)


@meter_api_bp.route('/meter/<int:meter_id>', methods=['GET'])
def show_meter_info(meter_id):
    '''
    Returns meter information as json object
    '''

    arw = ApiResponseWrapper()
    meter_schema = MeterSchema()

    try:
        meter = Meter.query.filter_by(meter_id=meter_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')
        return arw.to_json(None, 400)

    interval_coverage = request.args.get('interval_coverage')
    interval_count_start = request.args.get('interval_count_start')
    interval_count_end = request.args.get('interval_count_end')

    if not interval_coverage:
        interval_coverage = meter.get_all_intervals()

    if interval_count_start:
        try:
            interval_count_start = parser.parse(interval_count_start)
        except (TypeError, ValueError):
            arw.add_errors({
                'interval_count_start':
                'Not an accepted format for interval count start'
            })
            return arw.to_json(None, 400)

    if interval_count_end:
        try:
            interval_count_end = parser.parse(interval_count_end)
        except (TypeError, ValueError):
            arw.add_errors({
                'interval_count_end':
                'Not an accepted format for interval count end'
            })
            return arw.to_json(None, 400)

    # PENDING PROPS TO ADD TO THE RESPONSE
    # 'authorization_uid': 'NOT YET CREATED',
    # 'exports': 'NOT YET CREATED'

    meter_schema.context['start'] = interval_count_start
    meter_schema.context['end'] = interval_count_end
    meter_schema.context['coverage'] = interval_coverage

    results = meter_schema.dump(meter)

    return arw.to_json(results)


@meter_api_bp.route('/meter/meta', methods=['GET'])
def get_meter_schema():
    '''
    Returns meter schema as json object
    '''
    return jsonify(schema_data)


@meter_api_bp.route('/meter/<int:meter_id>', methods=['PUT'])
def update_meter(meter_id):
    '''
    Updates meter in database
    '''

    arw = ApiResponseWrapper()
    meter_schema = MeterSchema(exclude=['created_at', 'updated_at'])
    modified_meter = request.get_json()

    try:
        Meter.query.filter_by(meter_id=meter_id).one()
        modified_meter = meter_schema.load(modified_meter, session=db.session)
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

    results = meter_schema.dump(modified_meter)

    return arw.to_json(results)


@meter_api_bp.route('/meter', methods=['POST'])
def add_meter():
    '''
    Adds new meter to database
    '''

    arw = ApiResponseWrapper()
    meter_schema = MeterSchema(
        exclude=['meter_id', 'created_at', 'updated_at'])
    meter_json = request.get_json()

    try:
        new_meter = meter_schema.load(meter_json, session=db.session)
        db.session.add(new_meter)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = MeterSchema().dump(new_meter)

    return arw.to_json(result)
