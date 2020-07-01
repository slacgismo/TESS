from flask import Blueprint, request
from web.database import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from web.models.notification import Notification, NotificationSchema
from .response_wrapper import ApiResponseWrapper

notifications_api_bp = Blueprint('notifications_api_bp', __name__)

# test_data = [{
#     "pk":
#     1,
#     "email":
#     "one@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "TELECOMM_ALERTS",
#         "label": "Telecomm Alerts",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_LOAD",
#         "label": "Red Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_PRICE",
#         "label": "Red Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "YELLOW_ALARM_PRICE",
#         "label": "Yellow Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "CAPACITY_BOUNDS",
#         "label": "Capacity Bounds",
#         "is_active": False
#     }, {
#         "notification_type": "RESOURCE_DEPLETION",
#         "label": "Resource Depletion",
#         "is_active": False
#     }, {
#         "notification_type": "PRICE_ALERTS",
#         "label": "Price Alerts",
#         "is_active": False
#     }]
# }, {
#     "pk":
#     2,
#     "email":
#     "two@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "TELECOMM_ALERTS",
#         "label": "Telecomm Alerts",
#         "is_active": True
#     }, {
#         "notification_type": "RED_ALARM_LOAD",
#         "label": "Red Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_PRICE",
#         "label": "Red Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "YELLOW_ALARM_PRICE",
#         "label": "Yellow Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "CAPACITY_BOUNDS",
#         "label": "Capacity Bounds",
#         "is_active": True
#     }, {
#         "notification_type": "RESOURCE_DEPLETION",
#         "label": "Resource Depletion",
#         "is_active": False
#     }, {
#         "notification_type": "PRICE_ALERTS",
#         "label": "Price Alerts",
#         "is_active": False
#     }]
# }, {
#     "pk":
#     3,
#     "email":
#     "three@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "TELECOMM_ALERTS",
#         "label": "Telecomm Alerts",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_LOAD",
#         "label": "Red Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_PRICE",
#         "label": "Red Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "YELLOW_ALARM_PRICE",
#         "label": "Yellow Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "CAPACITY_BOUNDS",
#         "label": "Capacity Bounds",
#         "is_active": False
#     }, {
#         "notification_type": "RESOURCE_DEPLETION",
#         "label": "Resource Depletion",
#         "is_active": False
#     }, {
#         "notification_type": "PRICE_ALERTS",
#         "label": "Price Alerts",
#         "is_active": False
#     }]
# }, {
#     "pk":
#     4,
#     "email":
#     "four@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": True
#     }, {
#         "notification_type": "TELECOMM_ALERTS",
#         "label": "Telecomm Alerts",
#         "is_active": True
#     }, {
#         "notification_type": "RED_ALARM_LOAD",
#         "label": "Red Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_PRICE",
#         "label": "Red Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "YELLOW_ALARM_PRICE",
#         "label": "Yellow Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "CAPACITY_BOUNDS",
#         "label": "Capacity Bounds",
#         "is_active": True
#     }, {
#         "notification_type": "RESOURCE_DEPLETION",
#         "label": "Resource Depletion",
#         "is_active": False
#     }, {
#         "notification_type": "PRICE_ALERTS",
#         "label": "Price Alerts",
#         "is_active": True
#     }]
# }, {
#     "pk":
#     5,
#     "email":
#     "five@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "TELECOMM_ALERTS",
#         "label": "Telecomm Alerts",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_LOAD",
#         "label": "Red Alarm (Load)",
#         "is_active": False
#     }, {
#         "notification_type": "RED_ALARM_PRICE",
#         "label": "Red Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "YELLOW_ALARM_PRICE",
#         "label": "Yellow Alarm (Price)",
#         "is_active": False
#     }, {
#         "notification_type": "CAPACITY_BOUNDS",
#         "label": "Capacity Bounds",
#         "is_active": False
#     }, {
#         "notification_type": "RESOURCE_DEPLETION",
#         "label": "Resource Depletion",
#         "is_active": False
#     }, {
#         "notification_type": "PRICE_ALERTS",
#         "label": "Price Alerts",
#         "is_active": False
#     }]
# }, {
#     "pk":
#     6,
#     "email":
#     "six@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": True
#     }, {
#         "notification_type": "TELECOMM_ALERTS",
#         "label": "Telecomm Alerts",
#         "is_active": True
#     }, {
#         "notification_type": "RED_ALARM_LOAD",
#         "label": "Red Alarm (Load)",
#         "is_active": True
#     }, {
#         "notification_type": "RED_ALARM_PRICE",
#         "label": "Red Alarm (Price)",
#         "is_active": True
#     }, {
#         "notification_type": "YELLOW_ALARM_PRICE",
#         "label": "Yellow Alarm (Price)",
#         "is_active": True
#     }, {
#         "notification_type": "CAPACITY_BOUNDS",
#         "label": "Capacity Bounds",
#         "is_active": True
#     }, {
#         "notification_type": "RESOURCE_DEPLETION",
#         "label": "Resource Depletion",
#         "is_active": True
#     }, {
#         "notification_type": "PRICE_ALERTS",
#         "label": "Price Alerts",
#         "is_active": True
#     }]
# }]

@notifications_api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    '''
    Retrieves all notification objects
    '''
    
    notifications = Notification.query.all()
# "pk": ,
#     "email":
#     "six@tess.com",
#     "notifications": [{
#         "notification_type": "YELLOW_ALARM_LOAD",
#         "label": "Yellow Alarm (Load)",
#         "is_active": True
#     },
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
    notification_schema = NotificationSchema(only=fields_to_filter_on)
    results = notification_schema.dump(notifications, many=True)

    return arw.to_json(results)

@notifications_api_bp.route('/notification', methods=['PUT'])
def modify_notification():
    '''
    Updates one notification object in database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSchema(exclude=['alert_type_id', 'created_at'])
    modified_notification = request.get_json()

    try:
        modified_notification = notification_schema.load(
            modified_notification, session=db.session)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = notification_schema.dump(modified_notification,
                                           many=True)

    return arw.to_json(results)


@notifications_api_bp.route('/notification', methods=['POST'])
def add_notification():
    '''
    Adds new notification object to database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSchema(
        exclude=['notification_id', 'created_at', 'updated_at'])
    new_notification = request.get_json()

    try:
        new_notification = notification_schema.load(
            new_notification, session=db.session)
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