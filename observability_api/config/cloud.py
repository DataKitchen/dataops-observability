import os

# Flask specific settings: https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values
SECRET_KEY: str = os.environ["OBSERVABILITY_KEY_FLASK_SECRET"]
SERVER_NAME: str = os.environ["OBSERVABILITY_API_HOSTNAME"]

try:
    DEFAULT_JWT_EXPIRATION_SECONDS: float = float(os.environ["OBSERVABILITY_JWT_EXPIRATION_SECONDS"])
except Exception:
    pass
