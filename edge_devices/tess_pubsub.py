import time as t
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import heila_comms as hc
import config

# Expected payload to be received by edge devices when subscribing to a topic:
# {
#   "DeviceID": "TessEdgeController_NAME", "information":
#   [
#       {"resource": "solar", "real_power": "1000"},
#       {"resource": "battery", "real_power": "2000"},
#       {"resource": "ev", "real_power": "4000"}
#   ]
# }

def publish(client, topic, payload, Device_ID):
    payload = {'DeviceID': Device_ID, 'DeviceInformation': [payload]}
    try:
        client.publish(topic, json.dumps(payload), 1)
    except Exception as e:
        print('Publish error: ', e.message)
    print("Message published: ")
    print(payload)
    # client.disconnect() # Figure out if need to disconnect or not -> best pratices


def subscribe(client, topic):
    client.subscribe(topic, 1, customCallback)


def customCallback(client, userdata, message):
    payload = json.loads(message.payload)
    if payload['DeviceID'] == CLIENT_ID:
        # Generalize by including available resources in config file
        resources = payload['information']
        for r in resources:
            if r['resource'] == 'solar':
                retval = hc.heila_set_real_power(url=url, val=int(r['real_power']))
                print(retval)
                print("Received a new message: ")
                print('Real Power = ', r['real_power'])
            elif r['resource'] == 'ev':
                print('Call EV method to control real power to: ', r['real_power'])
            elif r['resource'] == 'battery':
                print('Call battery method to control real power to: ', r['real_power'])
            else:
                print('Not a valid resource for this edge device: ', r['resource'])
    print("--------------\n\n")


# AWS Info
ENDPOINT = config.ENDPOINT
CLIENT_ID = config.CLIENT_ID
PATH_TO_CERT = config.PATH_TO_CERT
PATH_TO_KEY = config.PATH_TO_KEY
PATH_TO_ROOT = config.PATH_TO_ROOT
TOPIC_PUBLISH = config.TOPIC_PUBLISH
TOPIC_SUBSCRIBE = config.TOPIC_SUBSCRIBE

# Edge Device Info
url = config.URL

# AWS IoT client config
myAWSIoTMQTTClient = AWSIoTPyMQTT.AWSIoTMQTTClient(CLIENT_ID)
myAWSIoTMQTTClient.configureEndpoint(ENDPOINT, 8883)
myAWSIoTMQTTClient.configureCredentials(PATH_TO_ROOT, PATH_TO_KEY, PATH_TO_CERT)

# # AWSIoTMQTTClient connection configuration -> Figure out which ones are required
# myAWSIoTMQTTClient.configureAutoReconnectBackoffTime(1, 32, 20)
# myAWSIoTMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
# myAWSIoTMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
# myAWSIoTMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
# myAWSIoTMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

myAWSIoTMQTTClient.connect()

# subscribing to topic
subscribe(myAWSIoTMQTTClient, TOPIC_SUBSCRIBE)

# publishing to topic
while True:
    payload = hc.heila_update(url=url)
    publish(myAWSIoTMQTTClient, TOPIC_PUBLISH, payload, CLIENT_ID)
    t.sleep(10) # Need to define how often to provide info updates
