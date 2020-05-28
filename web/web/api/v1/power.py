import random
import datetime
from flask import Blueprint
from .response_wrapper import ApiResponseWrapper

power_api_bp = Blueprint('power_api_bp', __name__)


def getRandomNumber():
    return random.randint(0, 100)


@power_api_bp.route('/power/system_load', methods=['GET'])
def get_power_system_load():
    """
    Retrieve Data for the System Load Chart
    """
    arw = ApiResponseWrapper()
    value_range = 30
    base = datetime.datetime.today()
    date_time_range = [
        base + datetime.timedelta(days=x) for x in range(value_range)
    ]
    results = {
        'one': {
            'x': date_time_range,
            'y': [getRandomNumber() for _ in range(0, value_range)]
        },
        'two': {
            'x': date_time_range,
            'y': [getRandomNumber() for _ in range(0, value_range)]
        }
    }
    return arw.to_json(results)


@power_api_bp.route('/power/resources', methods=['GET'])
def get_resources_load():
    """
    Retrieve Data for the Resources Chart
    """
    arw = ApiResponseWrapper()
    results = []
    return arw.to_json(results)
