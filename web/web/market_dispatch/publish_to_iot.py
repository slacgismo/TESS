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
    try:
        client.publish(topic, json.dumps(payload), 1)
    except Exception as e:
        print('Publish error: ', e.message)
    return
    # client.disconnect() # Figure out if need to disconnect or not -> best pratices
