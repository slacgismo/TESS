from web.database import db
from flask import request, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound
from .response_wrapper import ApiResponseWrapper
from web.models.device_event_source import (DeviceEventSource,
                                            DeviceEventSourceSchema,
                                            EventingDevice,
                                            EventingDeviceSchema)

des_api_bp = Blueprint('des_api_bp', __name__)


@des_api_bp.route('/device_event_source', methods=['GET'])
def get_des():
    '''
    Get DES
    '''
    arw = ApiResponseWrapper()
    des_schema = DeviceEventSourceSchema()
    des = DeviceEventSource.query.all()
    results = des_schema.dump(des, many=True)
    return arw.to_json(results)


@des_api_bp.route('/device_event_source/<int:des_id>', methods=['GET'])
def show_des(des_id):
    '''
    Returns des
    '''

    arw = ApiResponseWrapper()
    des_schema = DeviceEventSourceSchema()

    try:
        des = DeviceEventSource.query.filter_by(des_id=des_id).one()
    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')
        return arw.to_json(None, 400)

    results = des_schema.dump(des)

    return arw.to_json(results)


@des_api_bp.route('/device_event_source', methods=['POST'])
def add_des():
    '''
    Adds new event source entry
    '''

    arw = ApiResponseWrapper()
    des_schema = DeviceEventSourceSchema()
    des_json = request.get_json()

    try:
        new_des = des_schema.load(des_json, session=db.session)
        db.session.add(new_des)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = DeviceEventSourceSchema().dump(new_des)

    return arw.to_json(result)


@des_api_bp.route('/eventing_devices', methods=['GET'])
def get_evt_des():
    '''
    Get EVT DES
    '''
    arw = ApiResponseWrapper()
    des_schema = EventingDeviceSchema()
    des = EventingDevice.query.all()
    results = des_schema.dump(des, many=True)
    return arw.to_json(results)


@des_api_bp.route('/eventing_device/<int:des_id>', methods=['GET'])
def show_evt_des(des_id):
    '''
    Returns des
    '''

    arw = ApiResponseWrapper()
    des_schema = EventingDeviceSchema()

    try:
        des = EventingDevice.query.filter_by(des_id=des_id).one()
    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')
        return arw.to_json(None, 400)

    results = des_schema.dump(des)

    return arw.to_json(results)


@des_api_bp.route('/eventing_devices', methods=['POST'])
def add_evt_des():
    '''
    Adds new eventing device entry
    '''

    arw = ApiResponseWrapper()
    des_schema = EventingDeviceSchema()
    des_json = request.get_json()

    try:
        new_des = des_schema.load(des_json, session=db.session)
        db.session.add(new_des)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    result = EventingDeviceSchema().dump(new_des)

    return arw.to_json(result)
