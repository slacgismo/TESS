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
        meter_ids.append({'id': row.meter_id})

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

    #to store rate descriptions for json object
    rates = []
    #to store interval ids for interval_coverage 
    interval_ids = []

    for interval in meter.intervals:
        if interval.rate.description not in rates:
            rates.append(interval.rate.description)
        
    interval_ids.append(interval.interval_id)

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
                                  'rate': rates,
                                  'interval_count': meter.get_interval_count(), 
                                  'interval_coverage': Interval.get_interval_coverage(interval_ids), 
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
        return {'error': 'Not an existing meter id'}

    modified_meter = request.get_json()

    #keys required in json body
    required_keys = ['meter_id', 'utility_id', 'service_location_id', 'feeder', 'substation', 'meter_type', 'is_active', 'is_archived']
    
    #checks for missing keys, else throws error if missing
    for key in required_keys:
        if key not in modified_meter:
            message = 'Key Error - ' + key + ' is missing.'
            return jsonify({'error': message})

    #sets meter_type value equal to enum name
    modified_meter['meter_type'] = MeterType.check_value(modified_meter['meter_type'])
    if not modified_meter['meter_type']:
        return {'error': 'not accepted value for meter type'}
    
    try:
       modified_meter = meter_schema.load(modified_meter, session=db.session)
    except ValidationError as e:
        return e.messages, 422
    
    #adds meter to database if it doesn't conflict with database setup, else throws error
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'Conflict commiting changes with database'})

    #returns successful response code
    return jsonify({'success': 200})


#########################
##### ADD NEW METER #####
#########################


@app.route('/api/v1/meters', methods=['POST'])
def add_meter():
    '''Add new meter to database'''

    new_meter = request.get_json()

    #keys required in json body
    required_keys = ['meter_id', 'utility_id', 'service_location_id', 'feeder', 'substation', 'meter_type', 'is_active', 'is_archived']
    
    #checks for missing keys, else throws error if missing
    for key in required_keys:
        if key not in new_meter:
            message = 'Key Error - ' + key + ' is missing.'
            return jsonify({'error': message})
            
    #sets meter_type value equal to enum name
    new_meter['meter_type'] = MeterType.check_value(new_meter['meter_type'])
    if not new_meter['meter_type']:
        return {'error': 'not accepted value for meter type'}

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
        return jsonify({'error': 'Conflict adding data to database'})

    #returns successful response code
    return jsonify({'success': 200})
