import os

from flask import Flask

from common.api.flask_ext.authentication import ServiceAccountAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.cors import CORS
from common.api.flask_ext.database_connection import DatabaseConnection
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.api.flask_ext.health import Health
from common.api.flask_ext.logging import Logging
from common.api.flask_ext.timing import Timing
from event_api.helpers.health import readiness_probe
from event_api.routes import build_v1_routes, build_v2_routes

# create and configure the app
app = Flask(__name__, instance_relative_config=True)
Config(app, config_module="event_api.config")
CORS(app, allowed_methods=["GET", "POST"])
Logging(app)
ExceptionHandling(app)
Timing(app)
Health(app, prefix=app.config["API_PREFIX"], readiness_callback=readiness_probe)
DatabaseConnection(app)
ServiceAccountAuth(app)

# ensure the instance folder exists
os.makedirs(app.instance_path, exist_ok=True)
build_v1_routes(app, prefix=app.config["API_PREFIX"])
if os.environ.get("OBSERVABILITY_CONFIG") != "cloud":
    build_v2_routes(app, prefix=app.config["API_PREFIX"])
