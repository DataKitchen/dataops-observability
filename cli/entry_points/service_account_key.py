import logging
import sys
from argparse import ArgumentParser

from peewee import DoesNotExist

from cli.base import DatabaseScriptBase
from cli.lib import uuid_type
from common.auth.keys.service_key import generate_key
from common.entities import Project, Service

LOG = logging.getLogger(__name__)


class ServiceAccountKey(DatabaseScriptBase):
    """Generate a new authentication key for a given service."""

    subcommand: str = "service-key"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Generate a new authentication key for a service."
        parser.usage = "$ cli service-key [PROJECT_ID] [ALLOWED_SERVICE]..."
        parser.add_argument(
            "PROJECT_ID", nargs=1, type=uuid_type, help="The ID value of the Project for which the key will be valid"
        )
        parser.add_argument(
            "ALLOWED_SERVICE",
            nargs="+",
            default=[Service.EVENTS_API.value],
            help="Name of the service for which the key will be valid",
        )
        parser.add_argument("--name", default=None, help="A name to use for the key (must be unique per Project)")
        parser.add_argument("--description", default=None, help="A description of the Key's purpose")
        parser.add_argument(
            "--stdout",
            action="store_true",
            dest="std_out",
            help="Dump key to stdout so it can be easily redirected to a file",
        )

    def subcmd_entry_point(self) -> None:
        allowed_services = self.kwargs["ALLOWED_SERVICE"]
        project_id = self.kwargs["PROJECT_ID"]
        std_out = self.kwargs.get("std_out")
        name = self.kwargs.get("name")
        description = self.kwargs.get("description")

        try:
            project = Project.get_by_id(project_id)
        except DoesNotExist:
            LOG.error("#r<No Project with id> `#y<%s>` #r<exists.>", project_id)
            sys.exit(1)

        # We ARE eventually logging the key to the user, but this is intentional and okay. It's the only time it is
        # ever shown and is a valid exception to the semgrep rule.
        # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure
        LOG.info("Generating authentication key for: #c<%s> - #c<%s(%s)>", allowed_services, project.name, project.id)

        new_key = generate_key(
            allowed_services=allowed_services, project=project, name=name, description=description
        ).encoded_key

        if std_out:
            LOG.info("Service Key:")
            print(new_key)
        else:
            # nosemgrep: python.lang.security.audit.logging.logger-credential-leak.python-logger-credential-disclosure
            LOG.info("Service Key: \n#c<%s>", new_key)

        LOG.warning(
            "#y<Please take note of the above Service Account Key. This is the only time it will be shown and it "
            "cannot be retrieved!>"
        )

        sys.exit(0)
