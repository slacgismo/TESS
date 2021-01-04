import ast
import json
import time as t
import configuration
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT


def parseRealPower(message):
    ''' converts byte wtring to dict and retrieves a sunnyboy_inverter.calc_ac_power_kw
        data and timestamp as a dict
    '''
    payload_str = message.payload.decode("UTF-8")
    payload = ast.literal_eval(payload_str)
    power_data = payload["DeviceInformation"][0]["sunnyboy_inverter.calc_ac_power_kw"]
    return power_data

def customCallback(client, userdata, message):
    power_data = message.payload
    print("Received a new message: ")
    print(power_data)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# AWS Info
ENDPOINT = configuration.ENDPOINT
CLIENT_ID = configuration.CLIENT_ID
PATH_TO_CERT = configuration.PATH_TO_CERT
PATH_TO_KEY = configuration.PATH_TO_KEY
PATH_TO_ROOT = configuration.PATH_TO_ROOT
TOPIC_PUBLISH = configuration.TOPIC_PUBLISH
TOPIC_SUBSCRIBE = configuration.TOPIC_SUBSCRIBE

# Edge Device Info
url = configuration.URL

# AWS IoT client config
myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

myAWSIoTMQTTClient.connect()
# subscribing to topic
myAWSIoTMQTTClient.subscribe("DeviceEvents", 1, customCallback)

while True:
    None
