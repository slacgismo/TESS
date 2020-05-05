from web import app

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy 
from marshmallow import ValidationError

from .meter_api_schema import schema_data
from web.models.meter import Meter, MeterSchema, MeterType
from web.models.interval import Interval
from web.models.service_location import ServiceLocation
from web.database import db

#for error handling
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError

#for marshmallow
meter_schema = MeterSchema()


##########################
##### VIEW METER IDS #####
##########################


@app.route('/api/v1/meters', methods=['GET'])
def get_meter_ids():
    '''Returns meter ids as json object'''
    
    meter_ids = []

    meters = Meter.query.all()
    
    for row in meters:
        meter_ids.append({'meter_id': row.meter_id})

    return jsonify(meter_ids)


##########################
##### VIEW ONE METER #####
##########################


@app.route('/api/v1/meter/<string:meter_id>', methods=['GET'])
def show_meter_info(meter_id):
    '''Returns meter information as json object'''

    try:  
        meter = Meter.query.filter_by(meter_id=meter_id).one()
    except (MultipleResultsFound, NoResultFound):
        return {'Error': 'No results or multiple results found for meter.'}

    interval_coverage = request.args.get('interval_coverage')
    interval_count_start = request.args.get('interval_count_start')
    interval_count_end = request.args.get('interval_count_end')
    
    if not interval_coverage:
        interval_coverage = meter.get_all_intervals()

    if interval_count_start:
        try:
            interval_count_start = parser.parse(interval_count_start)
        except (TypeError, ValueError):
            return {'Error': 'Not an accepted format for interval count start and/or interval count end'}
    
    if interval_count_end:
        try:
            interval_count_end = parser.parse(interval_count_end) 
        except (TypeError, ValueError):
            return {'Error': 'Not an accepted format for interval count start and/or interval count end'} 

    meter_data = [{'meter_data': {'uid': meter.meter_id,
                                  'utility_uid': meter.utility_id, 
                                  'authorization_uid': 'NOT YET CREATED', 
                                  'user_id': 'NOT YET CREATED', 
                                  'meter_type': meter.meter_type.value, 
                                  'is_archived': meter.is_archived, 
                                  'is_active': meter.is_active, 
                                  'created': meter.created_at, 
                                  'service_location': meter.service_location_id, 
                                  'postal_code': meter.service_location.address.postal_code, 
                                  'map_location': meter.service_location.map_location, 
                                  'channels': [channel.setting for channel in meter.channels], 
                                  'feeder': meter.feeder, 
                                  'substation': meter.substation, 
                                  'rate': meter.get_rates(),
                                  'interval_count': meter.get_interval_count(interval_count_start, interval_count_end), 
                                  'interval_coverage': Interval.get_interval_coverage(interval_coverage), 
                                  'exports': 'NOT YET CREATED'}}] 

    return jsonify(meter_data)


#############################
##### VIEW METER SCHEMA #####
#############################


@app.route('/api/v1/meter/meta', methods=['GET'])
def get_meter_schema():
    '''Returns meter schema as json object'''
    
    return jsonify(schema_data)


#########################
##### MODIFY METER ######
#########################


@app.route('/api/v1/meter/<string:meter_id>', methods=['PUT'])
def update_meter(meter_id):
    '''Updates meter in database'''

    try:
        Meter.query.filter_by(meter_id=meter_id).one()
    except (MultipleResultsFound,NoResultFound):
        return {'Error': 'Not an existing meter id'}

    modified_meter = request.get_json()

    #sets meter_type value equal to enum name
    modified_meter['meter_type'] = MeterType.check_value(modified_meter['meter_type'])
    if not modified_meter['meter_type']:
        return {'Error': 'Not accepted value for meter type'}
    
    try:
       modified_meter = meter_schema.load(modified_meter, session=db.session)
    except ValidationError as e:
        return e.messages, 422
    
    #adds meter to database if it doesn't conflict with database setup, else throws error
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'Error': 'Conflict commiting changes with database (pk or fk issue).'})

    #returns successful response code
    return jsonify({'Success': 200})


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
