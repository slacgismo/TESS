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

def publish(client=myAWSIoTMQTTClient, topic=TOPIC_PUBLISH, payload="payload", Device_ID="DeviceID"):
    payload = {'DeviceID': Device_ID, 'DeviceInformation': payload}
    try:
        client.publish(topic, json.dumps(payload), 1)
    except Exception as e:
        print('Publish error: ', e.message)
    print("Message published: ")
    print(payload)
    # client.disconnect() # Figure out if need to disconnect or not -> best pratices



# # subscribing to topic
# subscribe(myAWSIoTMQTTClient, TOPIC_SUBSCRIBE)

# publishing to topic

# def request():
#     try:
#         retval = requests.get('https://www.google.com/').status_code
#         print('status code: ', retval)
#     except requests.exceptions.RequestException as e:
#         print('error: ', e)
#         t.sleep(5)
    # try:
    #     # Testing connection
    #     retval = requests.get('https://www.google.com/').status_code
    #     print('status code: ', retval)
    #     payload = [{'resource': 'solar', 'payload': hc.heila_update(url=url)},
    #                {'resource': 'battery', 'payload': sonnen_obj.get_batteries_status_json(serial=config.SONNEN_BATT)},
    #                {'resource': 'ev', 'payload': None}]
    #     publish(myAWSIoTMQTTClient, TOPIC_PUBLISH, payload, CLIENT_ID)
    #
    # except requests.exceptions.RequestException as e:
    #     print('error: ', e)
    #     print('Transfer control back to HEILA... Implement function - TBD')
    #     # to disable control from the power market, you need to send a POST request to the API endpoint /api/unsync .
    #     # To give back control, send a POST request to the API endpoint /api/sync
