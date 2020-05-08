from web import app

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy 
from marshmallow import ValidationError
import dateutil.parser as parser

from .response_wrapper import ApiResponseWrapper
from .meter_api_schema import schema_data
from web.models.meter import Meter, MeterSchema, MeterType
from web.models.interval import Interval
from web.models.service_location import ServiceLocation
from web.database import db

#for error handling
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError


@app.route('/api/v1/meters', methods=['GET'])
def get_meter_ids():
    """
    Return all meter objects
    TODO: support query string filtering on props like is_active/is_archived
    """    
    arw = ApiResponseWrapper()
    meter_schema = MeterSchema()
    meters = Meter.query.all()
    results = meter_schema.dump(meters, many=True)
    
    return arw.to_json(results)


@app.route('/api/v1/meter/<string:meter_id>', methods=['GET'])
def show_meter_info(meter_id):
    """
    Returns meter information as json object
    """
    arw = ApiResponseWrapper()
    meter_schema = MeterSchema(exclude=['service_location'])

    try:  
        meter = Meter.query.filter_by(meter_id=meter_id).one()
    
    except MultipleResultsFound:
        arw.add_errors({meter_id: 'Multiple results found for the given meter.'})
        return arw.to_json()
    
    except NoResultFound:
        arw.add_errors({meter_id: 'Multiple results found for the given meter.'})
        return arw.to_json()

    interval_coverage = request.args.get('interval_coverage')
    interval_count_start = request.args.get('interval_count_start')
    interval_count_end = request.args.get('interval_count_end')
    
    if not interval_coverage:
        interval_coverage = meter.get_all_intervals()

    if interval_count_start:
        try:
            interval_count_start = parser.parse(interval_count_start)
        except (TypeError, ValueError):
            arw.add_errors({'interval_count_start': 'Not an accepted format for interval count start'})
            return arw.to_json()
    
    if interval_count_end:
        try:
            interval_count_end = parser.parse(interval_count_end) 
        except (TypeError, ValueError):
            arw.add_errors({'interval_count_end': 'Not an accepted format for interval count end'})
            return arw.to_json()

    # PENDING PROPS TO ADD TO THE RESPONSE
    # 'authorization_uid': 'NOT YET CREATED', 
    # 'user_id': 'NOT YET CREATED', 
    # 'channels': [channel.setting for channel in meter.channels], 
    # 'feeder': meter.feeder, 
    # 'substation': meter.substation, 
    # 'rate': meter.get_rates(),
    # 'interval_count': meter.get_interval_count(interval_count_start, interval_count_end), 
    # 'interval_coverage': Interval.get_interval_coverage(interval_coverage), 
    # 'exports': 'NOT YET CREATED'

    results = meter_schema.dump(meter)
    return arw.to_json(results)


@app.route('/api/v1/meter/meta', methods=['GET'])
def get_meter_schema():
    """
    Returns meter schema as json object
    """
    return jsonify(schema_data)


@app.route('/api/v1/meter/<string:meter_id>', methods=['PUT'])
def update_meter(meter_id):
    '''Updates meter in database'''
    arw = ApiResponseWrapper()
    meter_schema = MeterSchema()
    modified_meter = request.get_json()
    
    try:
        Meter.query.filter_by(meter_id=meter_id).one()
        modified_meter = meter_schema.load(modified_meter, session=db.session)
        db.session.commit()
    
    except (MultipleResultsFound,NoResultFound):
        arw.add_errors('No result found or multiple results found')
    
    except IntegrityError as ie:
        db.session.rollback()
        arw.add_errors('Integrity error')
    
    except ValidationError as ve:
        db.session.rollback()
        # FIXME: args is already an array, which within arw.errors = [ [ { ... } ] ]
        # this is too much of a pain to traverse
        arw.add_errors(ve.args)

    if arw.has_errors():
        return arw.to_json()

    results = meter_schema.dump(modified_meter)
    return arw.to_json(results)


#########################
##### ADD NEW METER #####
#########################


@app.route('/api/v1/meter', methods=['POST'])
def add_meter():
    '''Add new meter to database'''

    new_meter = request.get_json()
            
    #sets meter_type value equal to enum name
    new_meter['meter_type'] = MeterType.check_value(new_meter['meter_type'])
    if not new_meter['meter_type']:
        return {'Error': 'Not accepted value for meter type'}

    try:
       new_meter = meter_schema.load(new_meter, session=db.session)
    except ValidationError as e:
        return e.messages, 422

    #adds meter to database if it doesn't conflict with database setup, else throws error
    try:
        db.session.add(new_meter)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'Conflict adding data to database (pk or fk issue).'})

    #returns successful response code
    return jsonify({'Success': 200})
