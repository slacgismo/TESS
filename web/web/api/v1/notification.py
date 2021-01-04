from flask import Blueprint, request
from web.database import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text, func
from sqlalchemy.sql import label
from itertools import groupby
from operator import attrgetter
from web.models.notification import Notification, NotificationSchema
from .response_wrapper import ApiResponseWrapper
from web.models.alert_type import AlertType, AlertTypeSchema

notifications_api_bp = Blueprint('notifications_api_bp', __name__)


@notifications_api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    '''
    Retrieves all notification objects
    '''
    # TODO: filter by utility, so only notifications for that utility appear

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Notification.__table__.columns:
                arw.add_errors({field: 'Invalid Notification field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    notifications = Notification.query.all()

    notification_schema = NotificationSchema(
        only=fields_to_filter_on,
        exclude=['created_by', 'created_at', 'updated_at'])

    results = notification_schema.dump(notifications, many=True)

    return arw.to_json(results)


@notifications_api_bp.route('notification',
                            methods=['PUT'])
def modify_notification():
    '''
    Updates one notification object in database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSchema(
        exclude=['created_at', 'updated_at'])
    modified_notification = request.get_json()
    try:
        modified_notification = notification_schema.load(modified_notification,
                                                         session=db.session)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = notification_schema.dump(modified_notification)

    return arw.to_json(results)


@notifications_api_bp.route('/notification', methods=['POST'])
def add_notification():
    '''
    Adds new notification object to database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSchema(
        exclude=['created_at', 'updated_at'])
    new_notification = request.get_json()

    try:
        new_notification = notification_schema.load(new_notification,
                                                    session=db.session)
        db.session.add(new_notification)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = NotificationSchema().dump(new_notification)

    return arw.to_json(results)


@notifications_api_bp.route('/notification', methods=['DELETE'])
def delete_notification():
    '''
    Adds new notification object to database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSchema(
        exclude=['alert_type_id', 'is_active', 'created_by', 'created_at', 'updated_at', 'email'])
    new_notification = request.get_json()

    try:
        new_notification = notification_schema.load(new_notification,
                                                    session=db.session)
        db.session.delete(new_notification)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = NotificationSchema().dump(new_notification)

    return arw.to_json(results)
