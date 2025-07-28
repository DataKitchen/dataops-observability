import os

from flask import Flask

from agent_api.helpers.health import readiness_probe
from agent_api.routes import build_v1_routes
from common.api.flask_ext.authentication import ServiceAccountAuth
from common.api.flask_ext.config import Config
from common.api.flask_ext.cors import CORS
from common.api.flask_ext.database_connection import DatabaseConnection
from common.api.flask_ext.exception_handling import ExceptionHandling
from common.api.flask_ext.health import Health
from common.api.flask_ext.logging import Logging
from common.api.flask_ext.timing import Timing

# Create and configure the app
app = Flask(__name__, instance_relative_config=True)
Config(app, config_module="agent_api.config")
CORS(app, allowed_methods=["POST"])
Logging(app)
ExceptionHandling(app)
Timing(app)
Health(app, prefix=app.config["API_PREFIX"], readiness_callback=readiness_probe)
DatabaseConnection(app)
ServiceAccountAuth(app)

os.makedirs(app.instance_path, exist_ok=True)  # Ensure the instance folder exists
build_v1_routes(app, prefix=app.config["API_PREFIX"])
