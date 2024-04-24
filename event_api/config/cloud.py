import os

# Flask specific settings: https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values
SECRET_KEY: str = os.environ["EVENTS_KEY_FLASK_SECRET"]
SERVER_NAME: str = os.environ["EVENTS_API_HOSTNAME"]
