import dateutil.parser as parser

from web.database import db
from marshmallow import ValidationError
from flask import jsonify, request, Blueprint
from .response_wrapper import ApiResponseWrapper
from web.models.pv import Pv, PvSchema

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


pv_api_bp = Blueprint('pv_api_bp', __name__)


@pv_api_bp.route('/pvs/', methods=['GET'])
def get_pvs():
    '''
    Returns all pv objects
    '''
    arw = ApiResponseWrapper()

    fields_to_filter_on = request.args.getlist('fields')

    if len(fields_to_filter_on) > 0:
        for field in fields_to_filter_on:
            if field not in Pv.__table__.columns:
                arw.add_errors({field: 'Invalid Pv field'})
                return arw.to_json(None, 400)
    else:
        fields_to_filter_on = None

    pv_schema = PvSchema(only=fields_to_filter_on)

    pvs = Pv.query.all()

    results = pv_schema.dump(pvs, many=True)

    return arw.to_json(results)


@pv_api_bp.route('/pv/<int:pv_id>', methods=['GET'])
def retrieve_pv_info(pv_id):
    '''
    Returns meter information as json object
    '''
    arw = ApiResponseWrapper()
    pv_schema = PvSchema(exclude=('meter_id',))

    try:  
        pv = Pv.query.filter_by(pv_id=pv_id).one()
    
    except MultipleResultsFound:
        arw.add_errors({pv_id: 'Multiple results found for the given pv.'})
        return arw.to_json(None, 400)
    
    except NoResultFound:
        arw.add_errors({pv_id: 'No results found for the given pv.'})
        return arw.to_json(None, 400)

    interval_coverage = request.args.get('interval_coverage')
    interval_count_start = request.args.get('interval_count_start')
    interval_count_end = request.args.get('interval_count_end')
    
    if not interval_coverage:
        interval_coverage = pv.meter.get_all_intervals()

    if interval_count_start:
        try:
            interval_count_start = parser.parse(interval_count_start)
        except (TypeError, ValueError):
            arw.add_errors({'interval_count_start': 'Not an accepted format for interval count start'})
            return arw.to_json()
    
    if interval_count_end:
        try:
            interval_count_end = parser.parse(interval_count_end) 
        except (TypeError, ValueError):
            arw.add_errors({'interval_count_end': 'Not an accepted format for interval count end'})
            return arw.to_json()

    pv_schema.context['start'] = interval_count_start
    pv_schema.context['end'] = interval_count_end
    pv_schema.context['coverage'] = interval_coverage
    results = pv_schema.dump(pv)
    return arw.to_json(results)


@pv_api_bp.route('/pv/<int:pv_id>', methods=['PUT'])
def update_pv(pv_id):
    '''Updates pv in database'''
    arw = ApiResponseWrapper()
    pv_schema = PvSchema(exclude=['created_at'])
    modified_pv = request.get_json()

    try:
        Pv.query.filter_by(pv_id=pv_id).one()
        modified_pv = pv_schema.load(modified_pv, session=db.session)
        db.session.commit()

    except (MultipleResultsFound,NoResultFound):
        arw.add_errors('No result found or multiple results found')
    
    except IntegrityError as ie:
        db.session.rollback()
        arw.add_errors('Integrity error')
    
    except ValidationError as ve:
        db.session.rollback()
        arw.add_errors(ve.messages)

    if arw.has_errors():
        return arw.to_json(None, 400)

    results = pv_schema.dump(modified_pv)

    return arw.to_json(results)


@pv_api_bp.route('/pv', methods=['POST'])
def add_pv():
    '''Adds new pv to database'''
    arw = ApiResponseWrapper()
    pv_schema = PvSchema(exclude=['pv_id', 'created_at', 'updated_at'])
    pv_json = request.get_json()
            
    try:
        new_pv = pv_schema.load(pv_json, session=db.session)
        db.session.add(new_pv)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        arw.add_errors({'pv_id': 'The given pv already exists.'})
        return arw.to_json(None, 400)
    
    except ValidationError as e:
        arw.add_errors(e.messages)
        return arw.to_json(None, 400)
    
    result = PvSchema().dump(new_pv)
    return arw.to_json(result)
