from flask import request, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.role import Role, RoleSchema

role_api_bp = Blueprint('role_api_bp', __name__)


@role_api_bp.route('/roles', methods=['GET'])
def get_role_ids():
    '''
    Retrieves all role objects
    '''

    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Role.__table__.columns:
                arw.add_errors({field: 'Invalid Role field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    roles = Role.query.all()
    role_schema = RoleSchema(only=fields_to_filter_on)
    results = role_schema.dump(roles, many=True)

    return arw.to_json(results)


@role_api_bp.route('/role', methods=['POST'])
def add_role():
    '''
    Adds new role object to database
    '''

    arw = ApiResponseWrapper()
    role_schema = RoleSchema(
        exclude=['role_id'])
    new_role = request.get_json()

    try:
        new_role = role_schema.load(new_role, session=db.session)
        db.session.add(new_role)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = RoleSchema().dump(new_role)

    return arw.to_json(results)
