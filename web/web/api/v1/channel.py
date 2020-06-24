from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.channel import Channel, ChannelSchema

channel_api_bp = Blueprint('channel_api_bp', __name__)

@channel_api_bp.route('/channel', methods=['POST'])
def add_channel():
    '''
    Adds new channel object to database
    '''

    arw = ApiResponseWrapper()
    channel_schema = ChannelSchema(exclude=['channel_id'])
    new_channel = request.get_json()

    try:
        new_channel = channel_schema.load(new_channel, session=db.session)
        db.session.add(new_channel)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = ChannelSchema().dump(new_channel)
    
    return arw.to_json(results)
