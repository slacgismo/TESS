import random
import datetime
from flask import Blueprint, request
from .response_wrapper import ApiResponseWrapper

power_api_bp = Blueprint('power_api_bp', __name__)


def getRandomNumber():
    return random.randint(0, 100)


@power_api_bp.route('/power/system_load/', methods=['GET'])
def get_power_system_load():
    '''
    Retrieves Data for the System Load Chart
    '''
    arw = ApiResponseWrapper()

    is_capacity = request.args.get("is_capacity", "FALSE").upper() == "TRUE"
    is_storage = request.args.get("is_storage", "FALSE").upper() == "TRUE"

    if is_capacity and is_storage:
        arw.add_errors("Cannot generate both capacity and storage data")
        return arw.to_json(None, 400)

    if not is_capacity and not is_storage:
        arw.add_errors(
            "Please specify which type of system load data to generate")
        return arw.to_json(None, 400)

    value_range = 30
    base = datetime.datetime.today()
    date_time_range = [
        base + datetime.timedelta(days=x) for x in range(value_range)
    ]

    results = {
        'labels': date_time_range,
        'one': [getRandomNumber() for _ in range(0, value_range)],
        'two': [getRandomNumber() for _ in range(0, value_range)]
    }

    return arw.to_json(results)


@power_api_bp.route('/power/resources', methods=['GET'])
def get_resources_load():
    '''
    Retrieve Data for the Resources Chart
    '''
    arw = ApiResponseWrapper()
    value_range = 3
    results = {
        'datasets': {
            'battery': [getRandomNumber() for _ in range(0, value_range)],
            'charger': [getRandomNumber() for _ in range(0, value_range)],
            'pv': [getRandomNumber() for _ in range(0, value_range)],
            'hvac': [getRandomNumber() for _ in range(0, value_range)],
            'hotWater': [getRandomNumber() for _ in range(0, value_range)]
        },
        'groupedDataset': {
            'unavailable': [],
            'available': [],
            'dispatched': []
        }
    }
    return arw.to_json(results)
