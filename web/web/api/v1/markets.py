import random
import datetime
import pandas as pd
from flask import Blueprint, request
from sqlalchemy import desc, asc
from .response_wrapper import ApiResponseWrapper

from web.models.hce_bids import HceBids, HceBidsSchema
from web.models.meter_interval import MeterInterval, MeterIntervalSchema
from web.models.market_interval import MarketInterval, MarketIntervalSchema


markets_api_bp = Blueprint('markets_api_bp', __name__)

@markets_api_bp.route('/markets/auction_market/', methods=['GET'])
def get_auction_market():
    '''
    Retrieves data for the auction market chart
    '''
    arw = ApiResponseWrapper()

    # latest market interval
    latest_market_interval = MarketInterval.query.order_by(desc('start_time')).first()
    latest_market_interval_start_time = latest_market_interval.start_time
    latest_market_interval_end_time = latest_market_interval.end_time

    hce_bids_schema = HceBidsSchema()
    hce_bids = HceBids.query.filter(HceBids.created_at > latest_market_interval_start_time).filter(HceBids.created_at < latest_market_interval_end_time)
    hce_bids = HceBids.query.all()
    hce = hce_bids_schema.dump(hce_bids, many=True)
    hce_bids = pd.DataFrame(hce)
    hce_bids.to_csv('web/charts_development/data/hce_bids.csv')

    meter_interval_schema = MeterIntervalSchema()
    meter_intervals = MeterInterval.query.all()
    result = meter_interval_schema.dump(meter_intervals, many=True)
    meter_intervals = pd.DataFrame(result)
    meter_intervals.to_csv('web/charts_development/data/meter_intervals.csv')

    # merge both data to match the x-axis
    data = hce_bids.merge(meter_intervals, on="q_bid", how="left")
    print(data)
    labels = list(data["q_bid"])
    # hce_bids
    one = list(data["p_bid_x"])
    # meter_intervals
    two = list(data["p_bid_y"])

    print("labels")
    print(type(labels))
    print(labels[0])

    results = {
        'labels': labels,
        'one': one,
        'two': two,
    }
    return arw.to_json(results)



@markets_api_bp.route('/markets/clearing_price/', methods=['GET'])
def get_clearing_price():
    '''
    Retrieves data for the clearing_price_overtime chart
    '''
    arw = ApiResponseWrapper()

    # date of 30 days ago
    thirty_days_ago = datetime.datetime.today() - datetime.timedelta(days=30)

    market_interval_schema = MarketIntervalSchema()
    market_interval = MarketInterval.query.order_by(asc('start_time')).filter(MarketInterval.start_time > thirty_days_ago)
    market_interval = MarketInterval.query.order_by(asc('start_time')).all()

    result = market_interval_schema.dump(market_interval, many=True)
    labels = [value["end_time"] for value in result]
    one = [value["p_clear"] for value in result]
    results = {
        'labels': labels,
        'one': one,
        'two': []
    }
    return arw.to_json(results)



@markets_api_bp.route('/markets/energy_demand/', methods=['GET'])
def get_historical_data():
    '''
    Retrieves data for the energy_demand chart
    '''
    arw = ApiResponseWrapper()

    # date of 30 days ago
    thirty_days_ago = datetime.datetime.today() - datetime.timedelta(days=30)

    market_interval_schema = MarketIntervalSchema()
    market_interval = MarketInterval.query.order_by(asc('start_time')).filter(MarketInterval.start_time > thirty_days_ago)
    market_interval = MarketInterval.query.order_by(asc('start_time')).all()

    result = market_interval_schema.dump(market_interval, many=True)
    labels = [value["end_time"] for value in result]
    one = [value["q_clear"] for value in result]
    results = {
        'labels': labels,
        'one': one,
        'two': []
    }
    return arw.to_json(results)
