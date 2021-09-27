import time as t
import json
import AWSIoTPythonSDK.MQTTLib as AWSIoTPyMQTT
import heila_comms as hc
import config
import sonnen_comms as sonnen
import requests
from datetime import datetime
import egauge_local_api as eg

# Expected payload to be received by edge devices when subscribing to a topic:
# {
#   "DeviceID": "TessEdgeController_NAME", "DeviceInformation":
#   [
#       {"resource": "solar", "payload": payload},
#       {"resource": "battery", "payload": payload},
#       {"resource": "ev", "payload": payload}
#   ]
# }


def publish(client, topic, payload, Device_ID):
    #TODO: Automate assignment of deviceID
    payload = {'DeviceID': Device_ID, 'DeviceInformation': payload}
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
    # {'DeviceID': 1, 'DeviceInformation': [{"resource": "solar", "payload": {"mode_dispatch": 1.0, "qmtp": 2.0}}, {"resource": "battery", "payload": {"mode_dispatch": 'None', "q_bid": 'None'}},{"resource": "ev", "payload": {"mode_dispatch": 'None', "q_bid": 'None'}}]}
    # print(message.payload)
    print("Received a new message: ")
    payload = json.loads(message.payload)
    resources = payload['DeviceInformation']
    for r in resources:
        if r['resource'] == 'solar':
            pwr = float(r['payload']['qmtp'])*float(r['payload']['mode_dispatch'])*1000
            try:
                retval = hc.heila_set_real_power(url='http://'+resource_map[str(payload['DeviceID'])], val=pwr)
                print(retval)
            except Exception as e:
                print('Error writing in Heila', e)
        elif r['resource'] == 'ev':
            print('Call EV method to control real power')
        elif r['resource'] == 'battery':
            print('Call battery method to control real power')
        else:
            print('Not a valid resource for this edge device: ', r['resource'])

    print("--------------\n\n")



def request():
    try:
        retval = requests.get('https://www.google.com/').status_code
        print('status code: ', retval)
    except requests.exceptions.RequestException as e:
        print('error: ', e)
        t.sleep(5)

# AWS Info
ENDPOINT = config.ENDPOINT
CLIENT_ID = config.CLIENT_ID
PATH_TO_CERT = config.PATH_TO_CERT
PATH_TO_KEY = config.PATH_TO_KEY
PATH_TO_ROOT = config.PATH_TO_ROOT
TOPIC_PUBLISH = config.TOPIC_PUBLISH
TOPIC_PUBLISH_TX = config.TOPIC_PUBLISH_TX
TOPIC_SUBSCRIBE = config.TOPIC_SUBSCRIBE

#TODO: Include all Heilas IP and configure based on the meter_id in the meter_intervals table
resource_map = {'1':config.IP_ADDRESS}

# Edge Device Info
url = config.URL
# Egauge Info
mode = 'ip'
ip = config.egauge_ip

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

# Initializing battery object
sonnen_obj = sonnen.SonnenApiInterface()

# publishing to topic
is_submitted = False
next_5min = (int(datetime.now().minute / 5) * 5) + 5
while True:
    if datetime.now().minute == next_5min:
        is_submitted = False
        print('submitted is False')
        next_5min = (int(datetime.now().minute / 5) * 5) + 5
        if next_5min == 60:
            next_5min = 0
        print('next5min: ', next_5min)
    if datetime.now().minute == next_5min - 1:
        if not is_submitted:
            print('Call publish method and submitted is True now')
            is_submitted = True
            time_start = (int(t.time()/300)+1)*300
            time_end = (int(t.time()/300)+2)*300
            try:
                # Testing connection
                retval = requests.get('https://www.google.com/').status_code
                print('status code: ', retval)
                ### Below code is for adding other resources
                # payload = [{'resource': 'solar', 'payload': hc.heila_update(url=url)},
                #            {'resource': 'battery', 'payload': sonnen_obj.get_batteries_status_json(serial=config.SONNEN_BATT)},
                #            {'resource': 'ev', 'payload': None}]
                # print('all payload done! ')
                ### DONE ###
                payload = hc.heila_update(url=url)
                if payload == None:
                    tessPV_payload = None
                else:
                    pv_info = payload["sunnyboy_inverter.calc_ac_power_kw"]
                    pv_power = pv_info['value']
                    # pv_time = datetime.fromtimestamp(pv_info['timestamp'] / 1000)
                    pv_time = datetime.fromtimestamp(time_start) # This is a temporary fix until figure out why heila is giving a time 5min ahead of current time
                    tessPV_payload = {'rate_id': 1, 'meter_id': 1, 'start_time': str(pv_time), 'end_time': str(datetime.fromtimestamp(time_end)),
                                      'e': pv_power / 12,
                                      'qmtp': pv_power, 'p_bid': 0, 'q_bid': 0, 'is_bid': 1, 'mode_dispatch': 0,
                                      'mode_market': 0}

                publish(myAWSIoTMQTTClient, TOPIC_PUBLISH, tessPV_payload, 1) # deviceID = 1 -> see TODO on def publish(): to automate this part
                # print(payload)
                print('Published ', datetime.now())
            except requests.exceptions.RequestException as e:
                print('error: ', e)
                print('Transfer control back to HEILA... Implement function - TBD')
                # to disable control from the power market, you need to send a POST request to the API endpoint /api/unsync .
                # To give back control, send a POST request to the API endpoint /api/sync
            payloadTransformer = eg.EgaugeInterface(mode=mode,endpoint=ip).processing_egauge_data()
            if payloadTransformer == None:
                tessTX_payload = None
            else:
                tx_power = -payloadTransformer["tess.Transformer"]
                tx_time = datetime.fromtimestamp(time_start) # This is a temporary fix until figure out why heila is giving a time 5min ahead of current time
                tessTX_payload = {'transformer_id':str(1),'q':str(tx_power), 'start_time': str(tx_time), 'end_time': str(datetime.fromtimestamp(time_end))}

            print('Transformer payload: ', tessTX_payload)
            publish(myAWSIoTMQTTClient, TOPIC_PUBLISH_TX, tessTX_payload, 1) # deviceID = 1 -> see TODO on def publish(): to automate this part
            # print(payload)
            print('Published ', datetime.now())
            t.sleep(10)

