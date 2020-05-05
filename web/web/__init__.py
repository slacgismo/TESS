from flask import Flask
from web.config import *
from web.extensions import db, bcrypt, migrate, ma
from web.auth.auth import auth_bp
from web.alerts.alerts import alerts_bp
from web.markets.markets import markets_bp
from web.power_dispatch.storage import storage_bp
from web.power_dispatch.capacity import capacity_bp
from web.constraints.constraints import constraints_bp
from web.cost_revenue.cost_revenue import cost_revenue_bp
from web.notifications.notifications import notifications_bp
from web.user_settings.user_settings import user_settings_bp

#enables trailing and non-trailing slash routes


def create_app(config_obj):
    """
    Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__, static_url_path='')
    app.config.from_object(config_obj)
    app.url_map.strict_slashes = False
    register_extensions(app)
    register_blueprints(app)
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
    app.register_blueprint(auth_bp, url_prefix='/')
    app.register_blueprint(alerts_bp, url_prefix='/alerts')
    app.register_blueprint(markets_bp, url_prefix='/markets')
    app.register_blueprint(capacity_bp, url_prefix='/power')
    app.register_blueprint(storage_bp, url_prefix='/power/storage')
    app.register_blueprint(constraints_bp, url_prefix='/constraints')
    app.register_blueprint(cost_revenue_bp, url_prefix='/cost_revenue')
    app.register_blueprint(notifications_bp, url_prefix='/notifications')
    app.register_blueprint(user_settings_bp, url_prefix='/user_settings')
    

app = create_app(DevelopmentConfig())

<<<<<<< HEAD
import web.api.v1.meter
=======

import web.api.v1.api
import web.api.v1.utility
>>>>>>> origin
