from flask import Flask, render_template
from web.config import *
from web.extensions import db, bcrypt, migrate, ma

# FRONT-END TEMPLATE BP ROUTES
from web.auth.auth import auth_bp
from web.alerts.alerts import alerts_bp
from web.markets.markets import markets_bp
from web.power_dispatch.storage import storage_bp
from web.power_dispatch.capacity import capacity_bp
from web.constraints.constraints import constraints_bp
from web.cost_revenue.cost_revenue import cost_revenue_bp
from web.notifications.notifications import notifications_bp
from web.user_settings.user_settings import user_settings_bp

# API V1 BP ROUTES
from web.api.v1.meter import meter_api_bp
from web.api.v1.power import power_api_bp
from web.api.v1.alert import alerts_api_bp
from web.api.v1.utility import utility_api_bp
from web.api.v1.user import users_api_bp
from web.api.v1.notification import notifications_api_bp
from web.api.v1.group import group_api_bp
from web.api.v1.service_location import service_location_api_bp
from web.api.v1.pv import pv_api_bp
from web.api.v1.meter_interval import meter_interval_api_bp
from web.api.v1.address import address_api_bp
from web.api.v1.home_hub import home_hub_api_bp

def page_not_found(e):
    return render_template('404.html'), 404


def create_app(config_obj):
    """
    Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__, static_url_path='')
    app.config.from_object(config_obj)
    register_extensions(app)
    register_blueprints(app)
    app.register_error_handler(404, page_not_found)
    return app


def register_extensions(app):
    """
    Register Flask extensions.
    """
    bcrypt.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)


def register_blueprints(app):
    """
    Register Flask blueprints.
    """
    # register frontend template blueprint routes
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(alerts_bp, url_prefix='/alerts')
    app.register_blueprint(markets_bp, url_prefix='/markets')
    app.register_blueprint(capacity_bp, url_prefix='/power')
    app.register_blueprint(storage_bp, url_prefix='/power/storage')
    app.register_blueprint(constraints_bp, url_prefix='/constraints')
    app.register_blueprint(cost_revenue_bp, url_prefix='/cost_revenue')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(user_settings_bp, url_prefix='/user_settings')

    # register api v1 blueprint routes
    app.register_blueprint(meter_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(power_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(alerts_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(utility_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(notifications_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(users_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(service_location_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(group_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(pv_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(meter_interval_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(address_api_bp, url_prefix='/api/v1/')
    app.register_blueprint(home_hub_api_bp, url_prefix="/api/v1/")

app = create_app(DevelopmentConfig())
