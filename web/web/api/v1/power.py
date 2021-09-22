import random
from datetime import datetime, timedelta
from flask import Blueprint, request
from .response_wrapper import ApiResponseWrapper
from sqlalchemy import desc
import pandas as pd


from web.models.transformer_interval import TransformerInterval, TransformerIntervalSchema
from web.models.pv import Pv, PvSchema
from web.models.meter_interval import MeterInterval, MeterIntervalSchema

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
    base = datetime.today()
    date_time_range = [
        base + timedelta(days=x) for x in range(value_range)
    ]

    transformer_interval_schema = TransformerIntervalSchema()
    # latest dattime - 1 day calculated
    last_transformer_interval = TransformerInterval.query.order_by(desc('start_time')).first()
    earliest = last_transformer_interval.start_time - timedelta(days = 1)
    transformer_interval = TransformerInterval.query.filter(TransformerInterval.start_time >= earliest)
    result = transformer_interval_schema.dump(transformer_interval, many=True)
    labels = [value["end_time"] for value in result]
    one = [value["q"] for value in result]
    # TODO: lable not printing
    results = {
        'labels': labels,
        'one': one
    }

    return arw.to_json(results)


@power_api_bp.route('/power/resources', methods=['GET'])
def get_resources_load():
    '''
    Retrieve Data for the Resources Chart
    '''
    arw = ApiResponseWrapper()
    value_range = 3

    # calculate 100% on y axis
    pv_schema = PvSchema()
    pv = Pv.query.filter_by(is_active = 1)
    result = pv_schema.dump(pv, many=True)
    hundred_percent = sum([value["q_rated"] for value in result])
    print(hundred_percent)

    meter_interval_schema = MeterIntervalSchema()
    meter_intervals = MeterInterval.query.all()
    result = meter_interval_schema.dump(meter_intervals, many=True)
    df = pd.DataFrame(result)
    df.to_csv('web/meter_intervals.csv')



    results = {
        'datasets': {
            'battery': [],
            'charger': [],
            'pv': [],
            'hvac': [],
            'hotWater': []
        },
        'groupedDataset': {
            'unavailable': [],
            'available': [],
            'dispatched': []
        }
    }
    return arw.to_json(results)
