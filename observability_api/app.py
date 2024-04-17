import os

from flask import Flask

from common.api.flask_ext.authentication import JWTAuth, ServiceAccountAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.cors import CORS
from common.api.flask_ext.database_connection import DatabaseConnection
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.api.flask_ext.health import Health
from common.api.flask_ext.logging import Logging
from common.api.flask_ext.timing import Timing
from common.api.flask_ext.url_converters import URLConverters
from observability_api.helpers.health import readiness_probe
from observability_api.routes import build_v1_routes

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
# This needs to be before any URLs are built.
URLConverters(app)
Config(app, config_module="observability_api.config")
DatabaseConnection(app)
CORS(app, allowed_methods=["GET", "POST", "PATCH", "DELETE"])
Logging(app)
ExceptionHandling(app)
Timing(app)
ServiceAccountAuth(app)
JWTAuth(app)
Health(app, prefix=app.config["API_PREFIX"], readiness_callback=readiness_probe)


# Ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)

views = build_v1_routes(app, prefix=app.config["API_PREFIX"])
