from web import app

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy 

from .meter_api_schema import schema_data
from web.models.meter import Meter, MeterSchema
from web.models.interval import Interval
from web.models.service_location import ServiceLocation

#for error handling routes
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.orm.exc import MultipleResultsFound


@app.route('/api/v1/meters', methods=['GET'])
def get_meter_ids():
    '''Returns meter ids as json object'''
    
    meter_ids = []

    meters = Meter.query.all()

    for row in meters:
        meter_ids.append({'id': row.meter_id})

    return jsonify(meter_ids)


@app.route('/api/v1/meter/<string:meter_id>', methods=['GET'])
def show_meter_info(meter_id):
    '''Returns meter information as json object'''
    
    try:  
        #retrieve for meter object matching meter_id
        meter = Meter.query.filter_by(meter_id=meter_id).one()

        #to store rate descriptions for json object
        rates = []

        #to store interval ids for interval_coverage 
        interval_ids = []

        for interval in meter.intervals:

            if interval.rate.description not in rates:
                rates.append(interval.rate.description)
        
            interval_ids.append(interval.interval_id)

        meter_data = [{meter.meter_id: {'utility_uid': meter.utility_id, 
                                    'authorization_uid': '?', 
                                    'user_id': '?', 
                                    'meter_type': meter.meter_type.value, 
                                    'is_archived': meter.is_archived, 
                                    'is_active': meter.is_active, 
                                    'created': '', 
                                    'service_location': meter.service_location_id, 
                                    'postal_code': meter.service_location.address.postal_code, 
                                    'map_location': meter.service_location.map_location, 
                                    'channels': [channel.setting for channel in meter.channels], 
                                    'feeder': meter.feeder, 
                                    'substation': meter.substation, 
                                    'rate': rates,
                                    'interval_count': meter.get_interval_count("2020-02-23", "2020-02-25"), 
                                    'interval_coverage': Interval.get_interval_coverage(interval_ids), 
                                    'exports': '?'}}] 

        return jsonify(meter_data)


    except (MultipleResultsFound, NoResultFound) as e:
        #no results or multiple results found 
        print(e)
        return 'error'


@app.route('/api/v1/meter/meta', methods=['GET'])
def get_meter_schema():
    '''Returns meter schema as json object'''
    
    return jsonify(schema_data)

# @app.route('/api/v1/meters/<string:meter_id>', methods=['PUT'])
# def modify_meter_info(meter_id):
#     try:  
#        # meter = Meter.query.filter_by(meter_id=meter_id).one()
#         req = request.get_json()
#         return jsonify(req)

#     except (MultipleResultsFound, NoResultFound) as e:
#         #no results or multiple results found 
#         print(e)
#         return 'error'


@app.route('/api/v1/meters', methods=['POST'])
def add_meter_info():
    '''Add new meter to database'''

    #retrieve input
    meter_id = request.form.get('meter_id')
    utility_id = int(request.form.get('utility_id'))
    service_location_id = request.form.get('service_location_id')
    feeder = request.form.get('feeder')
    substation = request.form.get('substation')
    meter_type = request.form.get('meter_type')
    is_active = request.form.get("is_active").upper() == "TRUE"
    is_archived = request.form.get("is_archived").upper() == "TRUE"

    try:
        service_location = ServiceLocation.query.filter_by(service_location_id=service_location_id).one()
        meter = Meter(meter_id=meter_id, utility_id=utility_id, service_location_id=service_location.service_location_id, feeder=feeder, substation=substation, meter_type=meter_type, is_active=is_active, is_archived=is_archived)
        db.session.add(meter)
        db.session.commit()

    except (MultipleResultsFound,NoResultFound) as e:
        #no results or multiple results found 
        print(e)
        return 'error'


@app.route('/api/v1/test', methods=['GET'])
def get_test():
    return jsonify({"testing": 12341234}), 400
