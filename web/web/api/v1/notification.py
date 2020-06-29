from flask import Blueprint, request
from web.database import db
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from web.models.utility_notification_setting import UtilityNotificationSetting, UtilityNotificationSettingSchema, NotificationSubscription, NotificationSubscriptionSchema
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
def get_notification_subscriptions():
    """
    Retrieves all notification subscription objects
    """
    arw = ApiResponseWrapper()

    notification_schema = NotificationSubscriptionSchema()
    notifications = NotificationSubscription.query.all()
    results = notification_schema.dump(notifications, many=True)

    return arw.to_json(results)


@notifications_api_bp.route('/notifications', methods=['PUT'])
def modify_notifications():
    '''
    Updates one notification object in database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSubscriptionSchema(exclude=['utility_id', 'utility_notification_setting_id', 'created_at'])
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


@notifications_api_bp.route('/notifications', methods=['POST'])
def add_notifications():
    '''
    Adds new notification object to database
    '''
    arw = ApiResponseWrapper()
    notification_schema = NotificationSubscriptionSchema(
        exclude=['notification_subscription_id', 'created_at', 'updated_at'])
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

    results = NotificationSubscriptionSchema().dump(new_notification)

    return arw.to_json(results)

@notifications_api_bp.route('/utility_notifications', methods=['POST'])
def add_service_location():
    '''
    Adds new service location object to database
    '''
    arw = ApiResponseWrapper()
    notification_schema = UtilityNotificationSettingSchema(
        exclude=['utility_notification_setting_id', 'created_at', 'updated_at'])
    new_utility_notification = request.get_json()

    try:
        new_utility_notification = notification_schema.load(
            new_utility_notification, session=db.session)
        db.session.add(new_utility_notification)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = UtilityNotificationSettingSchema().dump(new_utility_notification)

    return arw.to_json(results)