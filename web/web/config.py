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
    DB_SERVER = ''
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DB_USER = "tess_user"
    DB_PASSWORD = ""


class DevelopmentConfig(Config):
    DB_SERVER = 'localhost'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    DB_USER = "tess_user"
    DB_PASSWORD = "tess_db_password_local"
