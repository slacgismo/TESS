from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.alert import Alert, AlertSchema

alerts_api_bp = Blueprint('alerts_api_bp', __name__)

# test_data = [{
#     "date": "2020-01-01",
#     "time": "19:20",
#     "alert_type": "Capacity Bounds",
#     "description": "Lorem Ipsum dolor sit amet....",
#     "status": "Pending",
#     "assigned_to": "Operator 1",
#     "resolution": "A random resolution input"
# }, {
#     "date": "2020-01-02",
#     "time": "19:30",
#     "alert_type": "Resource Depletion",
#     "description":
#     "Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....",
#     "status": "Resolved",
#     "assigned_to": "Automated System",
#     "resolution": ""
# }, {
#     "date": "2020-01-21",
#     "time": "08:20",
#     "alert_type": "Price Alerts",
#     "description": "Lorem Ipsum dolor sit amet....",
#     "status": "Open",
#     "assigned_to": "SLAC Gismo",
#     "resolution": ""
# }, {
#     "date": "2020-01-22",
#     "time": "09:20",
#     "alert_type": "Capacity Bounds",
#     "description": "Lorem Ipsum dolor sit amet....",
#     "status": "Resolved",
#     "assigned_to": "SLAC Gismo",
#     "resolution": "I resolved this somehow"
# }, {
#     "date": "2020-01-23",
#     "time": "18:20",
#     "alert_type": "Resource Depletion",
#     "description":
#     "Lorem Ipsum dolor sit amet...Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet.....",
#     "status": "Resolved",
#     "assigned_to": "Automated System",
#     "resolution": "system recovered"
# }, {
#     "date": "2020-01-24",
#     "time": "19:20",
#     "alert_type": "Price Alerts",
#     "description": "Lorem Ipsum dolor sit amet....",
#     "status": "Open",
#     "assigned_to": "Operator 2",
#     "resolution": "Resolved"
# }, {
#     "date": "2020-01-25",
#     "time": "20:20",
#     "alert_type": "Capacity Bounds",
#     "description":
#     "Lorem Ipsum dolor sit amet..Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet......",
#     "status": "Pending",
#     "assigned_to": "Operator 1",
#     "resolution": "Resolved"
# }]


# @alerts_api_bp.route('/alerts', methods=['GET'])
# def get_alerts():
#     """
#     Retrieves all alert objects
#     """
#     arw = ApiResponseWrapper()

#     alert_schema = AlertSchema()
#     results = alert_schema.dump(test_data, many=True)

#     return arw.to_json(results)

@alerts_api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    '''
    Retrieves all alert objects
    '''
    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Alert.__table__.columns:
                arw.add_errors({field: 'Invalid Alert field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    alerts = Alert.query.all()
    alert_schema = AlertSchema(only=fields_to_filter_on, exclude=['alert_id', 'context_id', 'context'])
    results = alert_schema.dump(alerts, many=True)

    return arw.to_json(results)

@alerts_api_bp.route('/alert/<int:alert_id>', methods=['PUT'])
def update_alert(alert_id):
    '''
    Updates alert in database
    '''
    arw = ApiResponseWrapper()
    alert_schema = AlertSchema(exclude=['created_at'])
    modified_alert = request.get_json()

    try:
        Alert.query.filter_by(alert_id=alert_id).one()
        modified_alert = alert_schema.load(modified_alert,
                                           session=db.session)
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

    results = alert_schema.dump(modified_alert)

    return arw.to_json(results)

@alerts_api_bp.route('/alert', methods=['POST'])
def add_alert():
    '''
    Adds new alert object to database
    '''
    arw = ApiResponseWrapper()
    alert_schema = AlertSchema(
        exclude=['alert_id', 'created_at', 'updated_at'])
    new_alert = request.get_json()

    try:
        new_alert = alert_schema.load(
            new_alert, session=db.session)
        db.session.add(new_alert)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = AlertSchema(exclude=['alert_id', 'context', 'context_id']).dump(new_alert)

    return arw.to_json(results)