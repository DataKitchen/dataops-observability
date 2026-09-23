# Flask specific settings: https://flask.palletsprojects.com/en/latest/config/#builtin-configuration-values
PROPAGATE_EXCEPTIONS: bool | None = True
SECRET_KEY: str = "NOT_VERY_SECRET"

# Application settings
OAUTHLIB_INSECURE_TRANSPORT: bool = True
"""Determines whether or not to allow single-sign-on flow when not using https."""
