from flask import Flask, request, Blueprint
import logging
import requests
import json

sns_api_bp =  Blueprint('sns_api_bp', __name__)
logging.basicConfig(filename='sns.log', level=logging.INFO)

@sns_api_bp.route('/sns', methods = ['POST'])
def subscriber_information():
    # AWS sends JSON with text/plain mimetype
    try:
        js = json.loads(request.data)
    except ValueError as err:
        logging.error(err)
    hdr = request.headers.get('x-amz-sns-message-type')
    # subscribe to the SNS topic
    if hdr == 'Notification':
        parse_real_power(js['Message'])
    elif hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        r = requests.get(js['SubscribeURL'])
    logging.info('Success')
    return "OK\n"

def parse_real_power(message):
    ''' converts byte wtring to dict and retrieves a sunnyboy_inverter.calc_ac_power_kw
        data and timestamp as a dict
    '''
    payload_str = message.payload.decode('UTF-8')
    payload = ast.literal_eval(payload_str)
    power_data = payload['DeviceInformation'][0]['sunnyboy_inverter.calc_ac_power_kw']
    return power_data
