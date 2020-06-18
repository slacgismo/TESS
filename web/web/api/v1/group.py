from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.group import Group, GroupSchema

group_api_bp = Blueprint('group_api_bp', __name__)


@group_api_bp.route('/groups', methods=['GET'])
def get_group_ids():
    '''
    Retrieves all group objects
    '''

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Group.__table__.columns:
                arw.add_errors({field: 'Invalid Group field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    groups = Group.query.all()
    group_schema = GroupSchema(only=fields_to_filter_on)
    results = group_schema.dump(groups, many=True)

    return arw.to_json(results)


@group_api_bp.route('/group/<int:group_id>', methods=['GET'])
def show_group_info(group_id):
    '''
    Retrieves one group object
    '''

    arw = ApiResponseWrapper()
    group_schema = GroupSchema()

    try:
        group = Group.query.filter_by(group_id=group_id).one()

    except MultipleResultsFound:
        arw.add_errors(
            {group_id: 'Multiple results found for the given group id.'})
        return arw.to_json(None, 400)

    except NoResultFound:
        arw.add_errors({group_id: 'No results found for the given group id.'})
        return arw.to_json(None, 400)

    results = group_schema.dump(group)

    return arw.to_json(results)


@group_api_bp.route('/group/<int:group_id>', methods=['PUT'])
def modify_group(group_id):
    '''
    Updates one group object in database
    '''

    arw = ApiResponseWrapper()
    group_schema = GroupSchema(exclude=['created_at', 'user', 'role'])
    modified_group = request.get_json()

    try:
        Group.query.filter_by(group_id=group_id).one()
        modified_group = group_schema.load(modified_group, session=db.session)
        db.session.commit()

    except MultipleResultsFound:
        arw.add_errors(
            {group_id: 'Multiple results found for the given group id.'})
        return arw.to_json(None, 400)

    except NoResultFound:
        arw.add_errors({group_id: 'No results found for the given group id.'})
        return arw.to_json(None, 400)

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)

    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = group_schema.dump(modified_group)

    return arw.to_json(results)


@group_api_bp.route('/group', methods=['POST'])
def add_group():
    '''
    Adds new group object to database
    '''

    arw = ApiResponseWrapper()
    group_schema = GroupSchema(
        exclude=['created_at', 'user', 'role', 'group_id', 'updated_at'])
    new_group = request.get_json()

    try:
        new_group = group_schema.load(new_group, session=db.session)
        db.session.add(new_group)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors('Conflict while loading data')
        return arw.to_json(None, 400)

    except ValidationError as ve:
        arw.add_errors(ve.messages)
        return arw.to_json(None, 400)

    results = GroupSchema().dump(new_group)
    return arw.to_json(results)
