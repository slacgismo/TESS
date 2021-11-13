import time as t
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import web.iot_core.config as config
import requests

from web.models.meter_interval import MeterInterval
from web.models.hce_bids import HceBids
from web.models.transformer_interval import TransformerInterval
from web.config import *
from web.extensions import db
import sqlalchemy as sal
from sqlalchemy import insert
from sqlalchemy import create_engine
from datetime import datetime
import requests

# AWS Info
ENDPOINT = config.ENDPOINT
CLIENT_ID = config.CLIENT_ID
PATH_TO_CERT = config.PATH_TO_CERT
PATH_TO_KEY = config.PATH_TO_KEY
PATH_TO_ROOT = config.PATH_TO_ROOT
TOPIC_PUBLISH = config.TOPIC_PUBLISH
TOPIC_SUBSCRIBE_METER_INTERVAL = config.TOPIC_SUBSCRIBE_METER_INTERVAL
TOPIC_SUBSCRIBE_TRANSFORMER_INTERVAL = config.TOPIC_SUBSCRIBE_TRANSFORMER_INTERVAL

# AWS IoT client config
myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
myAWSIoTMQTTClient.connect()

if os.environ.get('FLASK_ENV', 'development') == 'production':
    db_config = ProductionConfig()
else:
    db_config = DevelopmentConfig()

def publish(client=myAWSIoTMQTTClient, topic=TOPIC_PUBLISH, payload="payload", device_id="DeviceID"):
    """Publish data to AWS IoTCore service

    Parameters:
        client (AWSIoTMQTTClient object): client configured above
        topic (string): topic devices subscribe to
        payload (object {[title: data]}): any object that is readible by the subscribing device
        device_id (string): corresponding device name that subscribes

    Returns:
        N/A: publishes the data to given topic
    """
    payload = {'DeviceID': device_id, 'DeviceInformation': payload}
    try:
        client.publish(topic, json.dumps(payload), 1)
    except Exception as e:
        print('Publish error: ', e.message)
    return
    # client.disconnect() # Figure out if need to disconnect or not -> best pratices


def sub_meter_intervals_data(client=myAWSIoTMQTTClient, topic=TOPIC_SUBSCRIBE_METER_INTERVAL):
    """Subscribe to IoT Core topic

    Parameters:
        client (AWSIoTMQTTClient object): client configured above
        topic (string): topic devices subscribe to

    Returns:
        N/A: callBack function
    """
    client.subscribe(topic, 1, meter_intervals_data_insert)
    return


def sub_transformer_intervals_data(client=myAWSIoTMQTTClient, topic=TOPIC_SUBSCRIBE_TRANSFORMER_INTERVAL):
    """Subscribe to IoT Core topic

    Parameters:
        client (AWSIoTMQTTClient object): client configured above
        topic (string): topic devices subscribe to

    Returns:
        N/A: callBack function
    """
    client.subscribe(topic, 1, transformer_interval_hce_bid_insert)
    return


def meter_intervals_data_insert(client, userdata, message):
    # publish data to the db when received
    print("HEY")
    engine = create_engine('mysql+pymysql://' + db_config.DB_USER + ":" + db_config.DB_PASSWORD + "@" + db_config.DB_SERVER + '/tess')
    conn = engine.connect()

    payload = json.loads(message.payload)["DeviceInformation"]

    conn.execute("INSERT INTO meter_intervals" + \
            " (meter_id, rate_id, start_time, end_time, e, qmtp," + \
            " p_bid, q_bid, mode_market, mode_dispatch, is_bid)" + \
            " VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                payload["meter_id"], payload["rate_id"],
                payload["start_time"], payload["end_time"],
                payload["e"], payload["qmtp"], payload["p_bid"],
                payload["q_bid"], payload["mode_market"],
                payload["mode_dispatch"], payload["is_bid"]
            )
    )
    conn.close()


def transformer_interval_hce_bid_insert(client, userdata, message):
    payload = json.loads(message.payload)["DeviceInformation"]
    # TODO: fix server link to production (remove 5000)
    server_link = f'http://{db_config.DB_SERVER}:5000'
    latest_transformer_interval = requests.get(f'{server_link}/api/v1/transformer_interval/latest')
    latest_transformer_interval_data = json.loads(latest_transformer_interval.content)["results"]["data"]
    load = float(payload["q"])
    try:
        import_capacity = latest_transformer_interval_data["import_capacity"]
    except:
        import_capacity = None
        pass
    # will be answered by Dave
    export_capacity =  999
    data_transformer_interval = {
        "import_capacity": import_capacity,
        "end_time": payload["end_time"],
        "export_capacity": export_capacity,
        "q": load,
        "start_time": payload["start_time"],
        "transformer_id": payload["transformer_id"],
        "unresp_load": None
    }

    # alert generation
    alert_settings = requests.get(f'{server_link}/api/v1/alert_setting')
    latest_alert_settings = json.loads(alert_settings.content)["results"]["data"]
    capacity_bound = latest_alert_settings["capacity_bound"]
    yellow_threshold = latest_alert_settings["yellow_alarm_percentage"]/100
    red_threshold = latest_alert_settings["red_alarm_percentage"]/100
    # if alert
    if (load*red_threshold > capacity_bound):
        alert = {
            "alert_type_id" : 2,
            "assigned_to" : "",
            "description" : "Red Alert - capacity bound: {capacity_bound}, load: {load}",
            "status" : "open",
            "context" : "Feeder",
            "context_id" : "hey",
            "resolution" : ""
        }
        requests.post(f'{server_link}/api/v1/alert', json=alert)
    elif (load*yellow_threshold > capacity_bound):
        alert = {
            "alert_type_id" : 2,
            "assigned_to" : "",
            "description" : f"Yellow Alert - capacity bound: {capacity_bound}, load: {load}",
            "status" : "open",
            "context" : "Feeder",
            "context_id" : "hey",
            "resolution" : ""
        }
        requests.post(f'{server_link}/api/v1/alert', json=alert)
    # p_bid needs to be coming in from HCE
    p_bid = 1
    # market_id needs to be coming in from somewhere, fine for MVP
    market_id = 1
    export_penalty = 0.01

    data_hce_bids_export = {
        "start_time": payload["start_time"],
        "end_time": payload["end_time"],
        "p_bid": p_bid - export_penalty,
        "q_bid": export_capacity,
        "is_supply": False,
        "comment": "export",
        "market_id": market_id
    }

    data_hce_bids_import = {
        "start_time": payload["start_time"],
        "end_time": payload["end_time"],
        "p_bid": p_bid,
        "q_bid": latest_transformer_interval_data["import_capacity"],
        "is_supply": True,
        "comment": "import",
        "market_id" : market_id

    }

    if (latest_transformer_interval_data["start_time"] == None):
        transformer_interval_id = latest_transformer_interval_data["transformer_interval_id"]
        requests.put(f'{server_link}/api/v1/transformer_interval/{transformer_interval_id}', json=data_transformer_interval)
    else:
        requests.post(f'{server_link}/api/v1/transformer_interval', json=data_transformer_interval)

    requests.post(f'{server_link}/api/v1/bids', json=data_hce_bids_export)
    requests.post(f'{server_link}/api/v1/bids', json=data_hce_bids_import)

    return
