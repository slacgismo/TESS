from flask import Flask, request, Blueprint
import json

sns_read_api_bp =  Blueprint('sns_read_api_bp', __name__)


@sns_read_api_bp.route('/sns_read', methods = ['GET', 'POST'])
def sns():
    # AWS sends JSON with text/plain mimetype
    try:
        js = json.loads(request.data)
    except:
        pass
    hdr = request.headers.get('x-amz-sns-message-type')
    # subscribe to the SNS topic
    if hdr == 'Notification':
        parseRealPower(js['Message'])
    else if hdr == 'SubscriptionConfirmation' and 'SubscribeURL' in js:
        return js['SubscribeURL']
    return 'OK\n'


def parseRealPower(message):
    ''' converts byte wtring to dict and retrieves a sunnyboy_inverter.calc_ac_power_kw
        data and timestamp as a dict
    '''
    payload_str = message.payload.decode("UTF-8")
    payload = ast.literal_eval(payload_str)
    power_data = payload["DeviceInformation"][0]["sunnyboy_inverter.calc_ac_power_kw"]
    return power_data
