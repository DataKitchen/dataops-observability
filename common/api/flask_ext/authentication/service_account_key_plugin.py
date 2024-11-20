__all__ = ["ServiceAccountAuth"]
import logging

from flask import g
from peewee import DoesNotExist
from werkzeug.exceptions import Unauthorized

from common.auth.keys.service_key import validate_key
from common.entities import Project

from .common import BaseAuthPlugin

LOG = logging.getLogger(__name__)


class ServiceAccountAuth(BaseAuthPlugin):
    """Service Account Key authentication plugin"""

    header_name = "ServiceAccountAuthenticationKey"

    @classmethod
    def pre_request_auth(cls) -> None:
        sa_key = cls.get_header_data()
        if sa_key is None:
            return

        key_data = validate_key(sa_key)
        if not key_data.valid:
            raise Unauthorized("Invalid service account key")

        try:
            g.project = Project.get_by_id(key_data.project_id)
            g.allowed_services = key_data.allowed_services
        except DoesNotExist as dne:
            raise Unauthorized("Invalid service account key") from dne
