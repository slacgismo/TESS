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
from web.models.market import Market, MarketSchema

net_revenue_api_bp = Blueprint('net_revenue_api_bp', __name__)

@net_revenue_api_bp.route('/net_revenue/cash_flow/', methods=['GET'])
def get_cash_flow():
    '''
    Retrieves data for the cash flow chart
    '''
    arw = ApiResponseWrapper()

    # last 24 hours
    one_day_ago = datetime.datetime.today() - datetime.timedelta(days=1)

    # market
    market_schema = MarketSchema()
    market = Market.query.all()
    market_result = market_schema.dump(market, many=True)
    market_df = pd.DataFrame(market_result).iloc[:1]

    # market_intervals
    market_interval_schema = MarketIntervalSchema()
    market_interval = MarketInterval.query.order_by(asc('start_time')).filter(MarketInterval.start_time > one_day_ago)
    market_interval_result = market_interval_schema.dump(market_interval, many=True)
    market_intervals_df = pd.DataFrame(market_interval_result)

    start_times = [value["start_time"] for value in market_interval_result]

    # meter_intervals
    meter_interval_schema = MeterIntervalSchema()
    meter_intervals = MeterInterval.query.filter(MeterInterval.start_time >= start_times[0])
    meter_interval_result = meter_interval_schema.dump(meter_intervals, many=True)
    meter_intervals_df = pd.DataFrame(meter_interval_result)

    # transformer_intervals
    transformer_interval_schema = TransformerIntervalSchema()
    transformer_intervals = TransformerInterval.query.filter(start_times[0] <= TransformerInterval.start_time)
    transformer_interval_result = transformer_interval_schema.dump(transformer_intervals, many=True)
    transformer_intervals_df = pd.DataFrame(transformer_interval_result)

    # hce_bids
    hce_bids_schema = HceBidsSchema()
    hce_bids = HceBids.query.filter(start_times[0] <= HceBids.start_time)
    hce_bid_result = hce_bids_schema.dump(hce_bids, many=True)
    hce_bids_df = pd.DataFrame(hce_bid_result)

    cash_flow = []
    cash_flow_integral = []
    for i, time in enumerate(start_times):
        cash_flow.append(get_cash_flow_from_data(time, transformer_intervals_df, meter_intervals_df, market_intervals_df, market_df, hce_bids_df))
        if i == 0:
            pass
        cash_flow_integral.append(cash_flow_integral[i-1] + cash_flow[i])

    results = {
        'cashFlow': {
            'labels': start_times,
            'one': cash_flow
        },
        'cashFlowIntegral' : {
            'labels': start_times,
            'one': cash_flow_integral
        }
    }

    return arw.to_json(results)


def get_cash_flow_from_data(start_time, transformer_interval, meter_interval, market_interval, market, hce_bids, market_id=1):
    p_clear = list(market_interval["p_clear"])
    RR = 0.20 # hard-coded, need to check
    # interval = market.loc[market_id]['ts']
    interval = 300 # hardcoded, will be replaced with above line
    unresp_load = transformer_interval['unresp_load'].loc[transformer_interval['start_time'] == start_time].iloc[-1]
    retail_income = RR*unresp_load*interval/3600. # price*energy
    import_power = transformer_interval['q'].loc[transformer_interval['start_time'] == start_time].iloc[-1]
    mc_WS = hce_bids['p_bid'].loc[(hce_bids['start_time'] == start_time) & (hce_bids['comment'] == 'import')].iloc[-1]
    import_expenses = mc_WS*import_power*interval/3600. # price*energy
    bids = meter_interval.loc[meter_interval['start_time'] == start_time]
    bids_interval = bids.merge(market_interval, on="start_time", how="left")
    cleared_bids = bids_interval.loc[bids_interval.p_bid <= bids_interval.p_clear]
    cleared_bids["payments_to_pv_owner"] = cleared_bids["p_clear"]*cleared_bids["q_bid"]*interval/3600.
    payments_to_pv_owners = cleared_bids["payments_to_pv_owner"].sum()
    cash_flow = retail_income - import_expenses - payments_to_pv_owners
    return cash_flow # cash flow / net revenue at time t
