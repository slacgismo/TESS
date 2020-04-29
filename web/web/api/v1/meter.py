from web import app

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy 

from .meter_api_schema import schema_data
from web.models.meter import Meter, MeterSchema, MeterType
from web.models.interval import Interval
from web.models.service_location import ServiceLocation

#for error handling
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from sqlalchemy.exc import IntegrityError


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

    except (MultipleResultsFound, NoResultFound) as e:
        print(e)
        return {'Error': 'No results or multiple results found for meter.'}

    meter_schema = MeterSchema()
    result = meter_schema.dump(meter)
    print(result)
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
                                  'interval_count': meter.get_interval_count("2020-02-23", "2020-02-25"), 
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
        meter = Meter.query.filter_by(meter_id=meter_id).one()

    except (MultipleResultsFound,NoResultFound) as e:
        print(e)
        return jsonify({'Error': 'No results or multiple results found for meter.'})

    #retrieve input
    new_meter = request.get_json()

    #keys required in json body
    required_keys = ['meter_id', 'utility_id', 'service_location_id', 'feeder', 'substation', 'meter_type', 'is_active', 'is_archived']
    
    #checks for missing keys, else throws error if missing
    for key in required_keys:
        if key not in new_meter:
            message = 'Key Error - ' + key + ' is missing.'
            print(message)
            return jsonify({'error': message})

    #checks to ensure meter_type value in an accepted enum value, else throws error
    if not MeterType.check_value(new_meter['meter_type']):
        message = 'Meter Type - ' + new_meter['meter_type'] + ' is not an enum value for meter types.'
        print(message)
        return jsonify({'error': message})

    #checks if utility_id is a numeric value, else throws error
    if new_meter['utility_id'].isdigit():
        meter.utility_id = int(new_meter['utility_id'])
    else:
        message = 'Value error - ' + new_meter['utility_id'] + ' is not a numeric value.'
        print(message)
        return jsonify({'error': message})

    meter.service_location_id = new_meter['service_location_id']
    meter.feeder = new_meter['feeder']
    meter.substation = new_meter['substation']
    meter.meter_type = new_meter['meter_type']
    meter.is_active = new_meter['is_active'].upper() == 'TRUE'
    meter.is_archived = new_meter['is_archived'].upper() == 'TRUE'

    #adds meter to database if it doesn't conflict with database setup, else throws error
    try:
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'Conflict commiting changes with database'})

    #returns successful response code
    return jsonify({'success': 200})


#########################
##### ADD NEW METER #####
#########################


@app.route('/api/v1/meters', methods=['POST'])
def add_meter():
    '''Add new meter to database'''

    #retrieve input
    new_meter = request.get_json()

    #keys required in json body
    required_keys = ['meter_id', 'utility_id', 'service_location_id', 'feeder', 'substation', 'meter_type', 'is_active', 'is_archived']
    
    #checks for missing keys, else throws error if missing
    for key in required_keys:
        if key not in new_meter:
            message = 'Key Error - ' + key + " is missing."
            print(message)
            return jsonify({'error': message})

    #checks to ensure meter_type value in an accepted enum value, else throws error
    if not MeterType.check_value(new_meter['meter_type']):
        message = 'Meter Type - ' + new_meter['meter_type'] + ' is not an enum value for meter types.'
        print(message)
        return jsonify({'error': message})

    #checks if utility_id is a numeric value, else throws error
    if new_meter['utility_id'].isdigit():
        utility_id = int(new_meter['utility_id'])
    else:
        message = 'Value error - ' + new_meter['utility_id'] + ' is not a numeric value.'
        print(message)
        return jsonify({'error': message})
    
    #set new meter object to be added to database
    meter = Meter(meter_id = new_meter['meter_id'], 
                  utility_id = utility_id, 
                  service_location_id = new_meter['service_location_id'], 
                  feeder = new_meter['feeder'], 
                  substation = new_meter['substation'], 
                  meter_type = new_meter['meter_type'], 
                  is_active = new_meter['is_active'].upper() == 'TRUE', 
                  is_archived = new_meter['is_archived'].upper() == 'TRUE')

    #adds meter to database if it doesn't conflict with database setup, else throws error
    try:
        db.session.add(meter)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print(e)
        return jsonify({'error': 'Conflict adding data to database'})

    #returns successful response code
    return jsonify({'success': 200})
