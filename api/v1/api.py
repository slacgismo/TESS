from flask import (Flask, jsonify)
from flask_sqlalchemy import SQLAlchemy 

app = Flask(__name__)

#insert connection to RDS database

@app.route('/api/v1/meter/meta', methods=['GET'])
def get_meter_schema():
    '''Returns meter schema as json object'''
    
    schema_data = []
 
    #retrieve schema data from db
    meter_schema = Schema.query.all()

    for row in meter_schema:
        schema_data.append({'attribute': row.attribute,
                            'format': row.format, 
                            'description': row.description, 
                            'example': row.example})

    return jsonify(schema_data)

    # alternate with hardcode:
    # schema_data = [{'attribute': 'uid', 
    #                 'format': 'uid string', 
    #                 'description': 'unique id for meter'},
    #                {'attribute': 'utility_uid',
    #                 'format': 'uid string',
    #                 'description': 'unique id for utility to which the meter belongs',
    #                 'example': 'xyz123p'},
    #                 {'attribute': 'authorization_uid',
    #                  'format': 'uid string',
    #                  'description': 'the authorization under which meter belongs',
    #                  'attribute': 'uid strin}
    #           ]

    