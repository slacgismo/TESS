import requests
from requests.exceptions import Timeout
import json
import config


def heila_set_real_power(url, val=10000):
    # val default value is set to 10000 so it does not curtail
    real_power_endpoint = '/api/set-real-power'
    payload = {'key':'real_power', 'value': str(val)}
    try:
        retval = requests.post(url+real_power_endpoint, json=payload, timeout=config.TIMEOUT)
    except requests.exceptions.RequestException as e:
        print('Request error: ', e)
        return None
    except Timeout:
        print('Heila timeout')
        return 'Timeout'

    return {'status_code': retval.status_code}


def heila_update(url):
    update = '/api/update'
    try:
        retval = requests.get(url + update, timeout=config.TIMEOUT)
    except requests.exceptions.RequestException as e:
        print('Request error: ', e)
        return None
    except Timeout:
        print('Heila timeout')
        return 'Timeout'

    if retval.status_code == 200:
        return json.loads(retval.text)['readings']
    else:
        return {'status_code': retval.status_code}


# Testing
# url = config.URL
# retval_update = heila_update(url=url)
# retval_real_power = heila_set_real_power(url=url, val=10000)


