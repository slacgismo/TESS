from flask import Flask
from flask_migrate import Migrate

app = Flask(__name__)

import web.api.v1.api