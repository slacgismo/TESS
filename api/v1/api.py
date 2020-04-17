from flask import (Flask, jsonify, request)
from flask_sqlalchemy import SQLAlchemy 

from meter_api_schema import schema_data
from models.meter_model import (Meter, Channel, Interval, Utility, Rate, Address, ServiceLocation, connect_to_db, db)

#for error handling routes - WIP
#from sqlalchemy.orm.exc import NoResultFound
#from sqlalchemy.orm.exc import MultipleResultsFound

app = Flask(__name__)


@app.route('/api/v1/meters', methods=['GET'])
def get_meter_ids():
    '''Returns meter ids as json object'''
    
    meter_ids = []

    meters = Meter.query.all()
    
    for row in meters:
        meter_ids.append({'id': row.meter_id})

    return jsonify(meter_ids)


@app.route('api/v1/meters/<string:meter_id>', methods=['GET'])
def show_meter_info(meter_id):
    '''Returns meter information as json object'''

    #retrieve for meter object matching meter_id
    meter = Meter.query.filter_by(meter_id=meter_id).one()
    
    #error handling if none is returned

    #user_id, authorization_id and exports are not in schema yet
    meter_data = {meter.meter_id: {
                'utility_uid': meter.utility_id,
                'authorization_uid': '',
                'user_id': '',
                'meter_type': meter.meter_type,
                'status': meter.status,
                'is_archived': meter.is_archived,
                'is_active': meter.is_active,
                'created': meter.created,
                'service_location': meter.service_location_id,
                'postal_code': meter.service_location.address.postal_code,
                'map_location': meter.service_location.map_location,
                'channel': meter.channel_id,
                'feeder': meter.feeder,
                'substation': meter.substation,
                'rate': meter.rate.description,
                'interval_count': '?',
                'interval_coverage': '?',
                'exports': ''}
                }

    return jsonify(meter_data)


@app.route('/api/v1/meter/meta', methods=['GET'])
def get_meter_schema():
    '''Returns meter schema as json object'''
    
    return jsonify(schema_data)

 @app.route('api/v1/meters/<string:meter_id>', methods=['PUT'])
 def modify_meter_info(meter_id):

#error handling (WIP)
#     try:  

#     except MultipleResultsFound, e:
#         print(e)

#     except NoResultFound, e:
#         print(e)

    meter = Meter.query.filter_by(meter_id=meter_id).one()
    req = request.get_json()
    return jsonify(req)


@app.route('/api/v1/meters/', methods=['POST'])
def add_meter_info():

    meter_id = request.json['meter_id']
    utility_id = request.json['utility_id']
    service_location_id = request.json['service_location_id']
    feeder = request.json['feeder']
    substation = request.json['substation']
    meter_type = request.json['meter_type']
    is_active = request.json['is_active']
    is_archived = request.json['is_archived']

if __name__ == '__main__':
    connect_to_db(app)
    app.run(debug=True, port=8080)