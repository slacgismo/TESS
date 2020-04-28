from flask import Flask
from web.config import *
from web.extensions import db, bcrypt, migrate, ma
from web.auth.auth import auth_bp

def create_app(config_obj):
    """
    Create application factory, as explained here: http://flask.pocoo.org/docs/patterns/appfactories/.
    :param config_object: The configuration object to use.
    """
    app = Flask(__name__)
    app.config.from_object(config_obj)
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


app = create_app(DevelopmentConfig())


import web.api.v1.api