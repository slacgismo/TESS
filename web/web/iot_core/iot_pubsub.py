import time as t
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import web.market_dispatch.config as config
import requests

# AWS Info
ENDPOINT = config.ENDPOINT
CLIENT_ID = config.CLIENT_ID
PATH_TO_CERT = config.PATH_TO_CERT
PATH_TO_KEY = config.PATH_TO_KEY
PATH_TO_ROOT = config.PATH_TO_ROOT
TOPIC_PUBLISH = config.TOPIC_PUBLISH
TOPIC_SUBSCRIBE = config.TOPIC_SUBSCRIBE

# AWS IoT client config
myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)
myAWSIoTMQTTClient.connect()

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
    print(payload)
    try:
        client.publish(topic, json.dumps(payload), 1)
    except Exception as e:
        print('Publish error: ', e.message)
    return
    # client.disconnect() # Figure out if need to disconnect or not -> best pratices


def sub_meter_intervals_data(client=myAWSIoTMQTTClient, topic=TOPIC_SUBSCRIBE):
    """Subscribe to IoT Core topic

    Parameters:
        client (AWSIoTMQTTClient object): client configured above
        topic (string): topic devices subscribe to

    Returns:
        N/A: callBack function
    """
    client.subscribe(topic, 1, meter_intervals_data_insert)
    return


from web.models.meter_interval import MeterInterval
from web.config import *
from web.extensions import db
import pyodbc
import sqlalchemy as sal
from sqlalchemy import insert
from sqlalchemy import create_engine

if os.environ.get('FLASK_ENV', 'development') == 'production':
    config = ProductionConfig()
else:
    config = DevelopmentConfig()

def meter_intervals_data_insert(client, userdata, message):
    # publish data to the db when received
    engine = create_engine('mysql+pymysql://' + config.DB_USER + ":" + config.DB_PASSWORD + "@" + config.DB_SERVER + '/tess')
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
