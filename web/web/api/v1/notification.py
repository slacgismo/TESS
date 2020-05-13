from flask import Blueprint
from web.models.notification import NotificationSchema
from .response_wrapper import ApiResponseWrapper


notifications_api_bp = Blueprint('notifications_api_bp', __name__)


test_data = [
    {
        "email": "one@tess.com",
        "notifications": [
            { "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)", "is_active": False },
            { "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts", "is_active": False },
            { "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)", "is_active": False },
            { "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)", "is_active": False },
            { "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)", "is_active": False },
            { "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds", "is_active": False },
            { "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion", "is_active": False },
            { "notification_type": "PRICE_ALERTS", "label": "Price Alerts", "is_active": False }
        ]
    },
    {
        "email": "two@tess.com",
        "notifications": [
            { "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)", "is_active": False },
            { "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts", "is_active": True },
            { "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)", "is_active": False },
            { "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)", "is_active": False },
            { "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)", "is_active": False },
            { "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds", "is_active": True },
            { "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion", "is_active": False },
            { "notification_type": "PRICE_ALERTS", "label": "Price Alerts", "is_active": False }
        ]
    },
    {
        "email": "three@tess.com",
        "notifications": [
            { "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)", "is_active": False },
            { "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts", "is_active": False },
            { "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)", "is_active": False },
            { "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)", "is_active": False },
            { "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)", "is_active": False },
            { "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds", "is_active": False },
            { "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion", "is_active": False },
            { "notification_type": "PRICE_ALERTS", "label": "Price Alerts", "is_active": False }
        ]
    },
    {
        "email": "four@tess.com",
        "notifications": [
            { "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)", "is_active": True },
            { "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts", "is_active": True },
            { "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)", "is_active": False },
            { "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)", "is_active": False },
            { "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)", "is_active": False },
            { "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds", "is_active": True },
            { "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion", "is_active": False },
            { "notification_type": "PRICE_ALERTS", "label": "Price Alerts", "is_active": True }
        ]
    },
    {
        "email": "five@tess.com",
        "notifications": [
            { "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)", "is_active": False },
            { "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts", "is_active": False },
            { "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)", "is_active": False },
            { "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)", "is_active": False },
            { "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)", "is_active": False },
            { "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds", "is_active": False },
            { "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion", "is_active": False },
            { "notification_type": "PRICE_ALERTS", "label": "Price Alerts", "is_active": False }
        ]
    },
    {
        "email": "six@tess.com",
        "notifications": [
            { "notification_type": "YELLOW_ALARM_LOAD", "label": "Yellow Alarm (Load)", "is_active": True },
            { "notification_type": "TELECOMM_ALERTS", "label": "Telecomm Alerts", "is_active": True },
            { "notification_type": "RED_ALARM_LOAD", "label": "Red Alarm (Load)", "is_active": True },
            { "notification_type": "RED_ALARM_PRICE", "label": "Red Alarm (Price)", "is_active": True },
            { "notification_type": "YELLOW_ALARM_PRICE", "label": "Yellow Alarm (Price)", "is_active": True },
            { "notification_type": "CAPACITY_BOUNDS", "label": "Capacity Bounds", "is_active": True },
            { "notification_type": "RESOURCE_DEPLETION", "label": "Resource Depletion", "is_active": True },
            { "notification_type": "PRICE_ALERTS", "label": "Price Alerts", "is_active": True }
        ]
    }
]

@notifications_api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """
    Retrieve all notification objects
    """
    arw = ApiResponseWrapper()

    notification_schema = NotificationSchema()
    results = notification_schema.dump(test_data, many=True)
    
    return arw.to_json(results)
