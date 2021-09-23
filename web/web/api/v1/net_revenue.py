import random
import datetime
import pandas as pd
from flask import Blueprint, request
from sqlalchemy import desc, asc
from .response_wrapper import ApiResponseWrapper
import numpy as np

from web.models.hce_bids import HceBids, HceBidsSchema
from web.models.meter_interval import MeterInterval, MeterIntervalSchema
from web.models.market_interval import MarketInterval, MarketIntervalSchema
from web.models.transformer_interval import TransformerInterval, TransformerIntervalSchema


net_revenue_api_bp = Blueprint('net_revenue_api_bp', __name__)

@net_revenue_api_bp.route('/net_revenue/cash_flow/', methods=['GET'])
def get_cash_flow():
    '''
    Retrieves data for the cash flow chart
    '''
    arw = ApiResponseWrapper()

    # last 24 hours
    one_day_ago = datetime.datetime.today() - datetime.timedelta(days=1)

    market_interval_schema = MarketIntervalSchema()
    market_interval = MarketInterval.query.order_by(asc('start_time')).filter(MarketInterval.start_time > one_day_ago)
    market_interval = MarketInterval.query.order_by(asc('start_time')).all()
    market_interval_result = market_interval_schema.dump(market_interval, many=True)
    df = pd.DataFrame(market_interval_result).to_csv('web/charts_development/data/cash_flow_market_interval.csv')

    start_times = [value["start_time"] for value in market_interval_result]
    p_clear = [value["p_clear"] for value in market_interval_result]

    meter_interval_schema = MeterIntervalSchema()
    meter_intervals = MeterInterval.query.filter(MeterInterval.start_time >= start_times[0])
    meter_interval_result = meter_interval_schema.dump(meter_intervals, many=True)
    df = pd.DataFrame(meter_interval_result).to_csv('web/charts_development/data/cash_flow_meter_interval.csv')
    # Calculate payments to PV owners: Sum all ((qmtp in TABLE meter_intervals for which p_bid <= p_clear))*p_clear
    payment_to_pv_owners = []
    for index, p in enumerate(p_clear):
        payment_to_pv_owners.append(np.sum([value["qmtp"] for value in meter_interval_result if value["start_time"] == start_times[index] and value["p_bid"] <= p])*p)

    # Calculate import costs: (q from TABLE transformer_intervals at start_time == t) * (p_bid in TABLE hce_bids at start_time == t)
    transformer_interval_schema = TransformerIntervalSchema()
    transformer_intervals = TransformerInterval.query.filter(start_times[0] <= TransformerInterval.start_time)
    transformer_interval_result = transformer_interval_schema.dump(transformer_intervals, many=True)
    df = pd.DataFrame(transformer_interval_result).to_csv('web/charts_development/data/cash_flow_transformer_interval.csv')
    transformer_q = [value["q"] for value in transformer_interval_result]

    hce_bids_schema = HceBidsSchema()
    hce_bids = HceBids.query.filter(start_times[0] <= HceBids.start_time)
    hce_bid_result = hce_bids_schema.dump(hce_bids, many=True)
    df = pd.DataFrame(hce_bid_result).to_csv('web/charts_development/data/cash_flow_hce_bid.csv')
    # Use p_bid for which is_supply = 1 if q >= 0
    # Use p_bid for which is_supply = 0 if q < 0
    for q in transformer_q:
        import_costs = [value["p_bid"] for value in hce_bid_result if ((value["is_supply"] == 1 and q >= 0) or (value["is_supply"] == 0 and q < 0))]


    # labels = [value["end_time"] for value in result]
    # one = [value["p_clear"] for value in result]

    results = {
        'labels': [],
        'one': [],
        'two': []
    }
    return arw.to_json(results)
