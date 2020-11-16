from flask import request, jsonify, Blueprint
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from .response_wrapper import ApiResponseWrapper
from web.database import db
from web.models.login import Login, LoginSchema

login_api_bp = Blueprint('login_api_bp', __name__)


@login_api_bp.route('/login/<int:login_id>', methods=['GET'])
def show_login_info(login_id):
    '''
    Retrieves one login object
    '''
    arw = ApiResponseWrapper()
    login_schema = LoginSchema()

    try:
        login = Login.query.filter_by(login_id=login_id).one()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = login_schema.dump(login)

    return arw.to_json(results)


@login_api_bp.route('login/<int:login_id>', methods=['PUT'])
def modify_login(login_id):
    '''
    Updates one login object in database
    '''

    arw = ApiResponseWrapper()
    login_schema = LoginSchema(exclude=[
        'updated_at', 'created_at'
    ])
    modified_login = request.get_json()

    try:
        Login.query.filter_by(login_id=login_id).one()
        modified_login = login_schema.load(modified_login, session=db.session)
        db.session.commit()

    except (MultipleResultsFound, NoResultFound):
        arw.add_errors('No result found or multiple results found')

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = login_schema.dump(modified_login)

    return arw.to_json(results)


@login_api_bp.route('/login', methods=['POST'])
def add_login():
    '''
    Adds new login object to database
    '''
    arw = ApiResponseWrapper()
    login_schema = LoginSchema(exclude=['login_id', 'created_at', 'updated_at'])
    new_login = request.get_json()

    try:
        new_login = login_schema.load(new_login, session=db.session)
        db.session.add(new_login)
        db.session.commit()

    except ValidationError as ve:
        arw.add_errors(ve.messages)

    except IntegrityError:
        arw.add_errors('Integrity error')

    if arw.has_errors():
        db.session.rollback()
        return arw.to_json(None, 400)

    results = LoginSchema().dump(new_login)

    return arw.to_json(results)
