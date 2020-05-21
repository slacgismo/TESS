# hardcode schema:
schema_data = [
    {
        'uid': {
            'format': 'uid string',
            'description': 'unique id for meter',
            'example': 'xyz123p'
        },
        'utility_uid': {
            'format': 'uid string',
            'description': 'unique id for utility to which the meter belongs',
            'example': 'xyz123p'
        },
        'authorization_uid': {
            'format': 'uid string',
            'description': 'the authorization under which meter belongs',
            'example': 'xyz123p'
        },
        'user_id': {
            'format': 'uid string',
            'description': 'unique id for meter owner',
            'example': 'xyz123p'
        },
        'meter_type': {
            'format': '',
            'description': '',
            'example': ''
        },
        'status': {
            'format': 'string',
            'description': '',
            'example': ''
        },
        'is_archived': {
            'format': 'boolean',
            'description': 'whether meter data is archived',
            'example': 'True or False'
        },
        'is_active': {
            'format': 'boolean',
            'description': 'whether meter data is active',
            'example': 'True or False'
        },
        'created': {
            'format': 'ISO8601 TIMESTAMP',
            'description': 'when the meter was created',
            'example': '2020-03-20T11:21:33.123456+00:00'
        },
        'service_location': {
            'format': 'string',
            'description': '',
            'example': ''
        },
        'postal_code': {
            'format': 'string',
            'description': '',
            'example': ''
        },
        'map_location': {
            'format': '?',
            'description': '',
            'example': ''
        },
        'channel': {
            'format': 'integer',
            'description': '',
            'example': '1 or 3'
        },
        'feeder': {
            'format': 'integer?',
            'description': '',
            'example': ''
        },
        'substation': {
            'format': 'integer?',
            'description': '',
            'example': ''
        },
        'rate': {
            'format': 'string',
            'description': 'tariff',
            'example': ''
        },
        'interval_count': {
            'format': 'integer',
            'description': 'number of intervals collected',
            'example': '123456'
        },
        'interval_coverage': {
            'format': 'list of ISO8601 tuples',
            'description': 'timespans covered by intervals collected',
            'example': ''
        },
        'exports': {
            'format': 'list of name, URL tuples',
            'description': 'list of name and URLs to various meter data downloads',
            'example': ''
        }
    }
]
