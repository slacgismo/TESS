from flask import Blueprint, request
from web.database import db
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from web.models.alert_type import AlertType, AlertTypeSchema
from .response_wrapper import ApiResponseWrapper

alert_types_api_bp = Blueprint('alert_types_api_bp', __name__)


@alert_types_api_bp.route('/alert_types', methods=['GET'])
def get_alert_types():
    '''
    Retrieves all alert type objects
    '''
    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in AlertType.__table__.columns:
                arw.add_errors({field: 'Invalid Alert Type field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    alert_types = AlertType.query.all()
    alert_type_schema = AlertTypeSchema(only=fields_to_filter_on)
    results = alert_type_schema.dump(alert_types, many=True)

    return arw.to_json(results)


@alert_types_api_bp.route('/alert_type/<int:alert_type_id>', methods=['PUT'])
def update_alert_type(alert_type_id):
    '''
    Updates alert type in database
    '''
    arw = ApiResponseWrapper()
    alert_type_schema = AlertTypeSchema(exclude=['created_at'])
    modified_alert_type = request.get_json()

    try:
        AlertType.query.filter_by(alert_type_id=alert_type_id).one()
        modified_alert_type = alert_type_schema.load(modified_alert_type,
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

    results = alert_type_schema.dump(modified_alert_type)

    return arw.to_json(results)


@alert_types_api_bp.route('/alert_type', methods=['POST'])
def add_alert_type():
    '''
    Adds new alert type object to database
    '''
    arw = ApiResponseWrapper()
    alert_type_schema = AlertTypeSchema(
        exclude=['alert_type_id', 'created_at', 'updated_at'])
    new_alert_type = request.get_json()

    try:
        new_alert_type = alert_type_schema.load(new_alert_type,
                                                session=db.session)
        db.session.add(new_alert_type)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = AlertTypeSchema().dump(new_alert_type)

    return arw.to_json(results)
