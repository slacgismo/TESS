from flask import Blueprint, request
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import desc

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.alert_setting import AlertSetting, AlertSettingSchema

alert_setting_api_bp = Blueprint('alert_setting_api_bp', __name__)

@alert_setting_api_bp.route('/alert_setting', methods=['GET'])
def get_alert_setting():
    '''
    Retrieves alert_settings
    '''
    # TO DO: filter by utility

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in AlertSetting.__table__.columns:
                arw.add_errors({field: 'Invalid Alert field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    alert_setting = AlertSetting.query.order_by(desc('updated_at')).first()
    alert_setting_schema = AlertSettingSchema()
    results = alert_setting_schema.dump(alert_setting, many=False)
    return arw.to_json(results)


@alert_setting_api_bp.route('/alert_setting', methods=['POST'])
def add_alert_setting():
    '''
    Adds new alert_settings object in database
    '''
    arw = ApiResponseWrapper()
    alert_setting_schema = AlertSettingSchema(
        exclude=['created_at', 'updated_at'])
    new_alert_setting = request.get_json()
    try:
        new_alert_setting = alert_setting_schema.load(new_alert_setting,
                                                         session=db.session)
        db.session.add(new_alert_setting)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = alert_setting_schema.dump(new_alert_setting)
    return arw.to_json(results)
