import os
from datetime import timedelta

JWT_ACCESS_EXPIRES = timedelta(minutes=120)
JWT_REFRESH_EXPIRES = timedelta(days=30)

class Config(object):
    """Base config, uses staging database server."""
    DEBUG = True
    TESTING = True
    DB_SERVER = ''
    DB_USER = ''
    DB_PASSWORD = ''

    @property
    def SQLALCHEMY_DATABASE_URI(self):
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_SERVER}/tess"


class ProductionConfig(Config):
    """Uses production database server."""
    DB_SERVER = os.environ.get('DB_SERVER', None)
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DB_USER = os.environ.get('DB_USER', None)
    DB_PASSWORD = os.environ.get('DB_PASSWORD', None)


class DevelopmentConfig(Config):
    DB_SERVER = 'localhost'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DB_USER = "tess_user"
    DB_PASSWORD = "tess_db_password_local"
    JWT_SECRET_KEY = os.urandom(12).hex()
    JWT_ACCESS_TOKEN_EXPIRES = JWT_ACCESS_EXPIRES
    JWT_REFRESH_TOKEN_EXPIRES = JWT_REFRESH_EXPIRES
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    JWT_TOKEN_LOCATION = ['cookies', 'headers', 'query_string']
    # JWT_COOKIE_CSRF_PROTECT = False
    JWT_CSRF_IN_COOKIES = False
    # JWT_CSRF_CHECK_FORM = False
    # JWT_ACCESS_COOKIE_PATH = '/'
    # JWT_COOKIE_SECURE = False
