from flask import Blueprint
from web.models.alert import AlertSchema
from .response_wrapper import ApiResponseWrapper


alerts_api_bp = Blueprint('alerts_api_bp', __name__)

test_data = [
    {
        "date": "2020-01-01",
        "time": "19:20",
        "alert_type": "Capacity Bounds",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Pending",
        "assigned_to": "Operator 1",
        "resolution": "A random resolution input"
    },
    {
        "date": "2020-01-02",
        "time": "19:30",
        "alert_type": "Resource Depletion",
        "description": "Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....",
        "status": "Resolved",
        "assigned_to": "Automated System",
        "resolution": ""
    },
    {
        "date": "2020-01-21",
        "time": "08:20",
        "alert_type": "Price Alerts",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Open",
        "assigned_to": "SLAC Gismo",
        "resolution": ""
    },
    {
        "date": "2020-01-22",
        "time": "09:20",
        "alert_type": "Capacity Bounds",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Resolved",
        "assigned_to": "SLAC Gismo",
        "resolution": "I resolved this somehow"
    },
    {
        "date": "2020-01-23",
        "time": "18:20",
        "alert_type": "Resource Depletion",
        "description": "Lorem Ipsum dolor sit amet...Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet.....",
        "status": "Resolved",
        "assigned_to": "Automated System",
        "resolution": "system recovered"
    },
    {
        "date": "2020-01-24",
        "time": "19:20",
        "alert_type": "Price Alerts",
        "description": "Lorem Ipsum dolor sit amet....",
        "status": "Open",
        "assigned_to": "Operator 2",
        "resolution": "Resolved"
    },
    {
        "date": "2020-01-25",
        "time": "20:20",
        "alert_type": "Capacity Bounds",
        "description": "Lorem Ipsum dolor sit amet..Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet....Lorem Ipsum dolor sit amet......",
        "status": "Pending",
        "assigned_to": "Operator 1",
        "resolution": "Resolved"
    }
]

@alerts_api_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """
    Retrieves all alert objects
    """
    arw = ApiResponseWrapper()

    alert_schema = AlertSchema()
    results = alert_schema.dump(test_data, many=True)
    
    return arw.to_json(results)
