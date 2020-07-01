from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.alert import Alert, AlertSchema

alerts_api_bp = Blueprint('alerts_api_bp', __name__)

@alerts_api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    '''
    Retrieves all alert objects
    '''
    # TO DO: filter by utility, so only alerts for that utility appear

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
    alert_schema = AlertSchema(only=fields_to_filter_on, exclude=['context_id', 'context'])
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
    print(new_alert)
    results = AlertSchema(exclude=['alert_id', 'context', 'context_id']).dump(new_alert)
    print(results)
    return arw.to_json(results)