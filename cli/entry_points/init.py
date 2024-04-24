import base64
import json
import logging
import sys
from argparse import ArgumentParser
from uuid import uuid4

from cli.base import DatabaseScriptBase
from common.auth.keys.lib import hash_value
from common.auth.keys.service_key import generate_key
from common.entities import DB, Action, AuthProvider, Company, Organization, Project, User
from common.model import create_all_tables

USER_FIELDS = ["name", "email", "username", "password"]

LOG = logging.getLogger(__name__)


def collect_user_input(fields: list[str]) -> dict[str, str]:
    res = {}
    try:
        for field in fields:
            while field not in res:
                if value := input(f"{field.capitalize()!s: >20}: "):
                    res[field] = value
    except KeyboardInterrupt:
        print("--\n")  # Moving the cursor back to the start
        raise OperationAborted("Operation aborted by the user")
    return res


def read_json_input(fields: list[str]) -> dict[str, str]:
    res = {}
    payload = input()

    if not payload:
        raise OperationAborted("This command requires a JSON input")
    try:
        json_input = json.loads(payload)
        for field in fields:
            res[field] = json_input[field]
    except KeyError as e:
        raise OperationAborted(f"'{e}' not found in the input data")
    except Exception:
        raise OperationAborted("Invalid input data")
    return res


class OperationAborted(Exception):
    pass


class Initialize(DatabaseScriptBase):
    """Provides initial data and configuration."""

    subcommand: str = "init"

    @staticmethod
    def args(parser: ArgumentParser) -> None:
        parser.description = "Provides initial data and configuration"
        parser.usage = "$ cli init"
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            help="Removes previously existing data, if any.",
        )
        parser.add_argument(
            "-t",
            "--tables",
            action="store_true",
            help="Initializes the database tables.",
        )
        parser.add_argument(
            "-d",
            "--data",
            action="store_true",
            help="Populate the essential data needed for the platform to run.",
        )
        parser.add_argument(
            "-e",
            "--demo",
            action="store_true",
            help="Populate the data needed for the Demo script",
        )
        parser.add_argument(
            "-j",
            "--json",
            action="store_true",
            help="Outputs the generated IDs in JSON format when successful",
        )

    def subcmd_entry_point(self) -> None:
        try:
            self.initialize_database()
        except OperationAborted as e:
            LOG.info("Operation #y<ABORTED>: %s", e)
            sys.exit(1)
        except Exception as e:
            LOG.error("Operation #r<FAILED>: %s", e)
            sys.exit(2)
        else:
            LOG.info("Operation #g<SUCCEEDED>")

    def initialize_database(self) -> None:
        if not (self.kwargs.get("tables") or self.kwargs.get("data") or self.kwargs.get("demo")):
            raise OperationAborted("Either --data or --demo or --tables has to be set.")

        if self.kwargs.get("tables"):
            if self.kwargs.get("force"):
                raise OperationAborted("The --force option can not be used when creating the tables.")

            if DB.get_tables():
                raise OperationAborted("The database already has tables.")

        if self.kwargs.get("data") or self.kwargs.get("demo"):
            if DB.get_tables() and Company.select().count() > 0:
                if self.kwargs.get("force"):
                    LOG.warning("#r<The Database is not empty. Previously existing data will be erased!>")
                else:
                    raise OperationAborted("The Database is not empty.")

            if self.kwargs.get("json"):
                LOG.info("Waiting for the JSON input data: %s", ", ".join(USER_FIELDS))
                user_data = read_json_input(USER_FIELDS)
            else:
                print("\nPlease enter the default user data:\n")
                user_data = collect_user_input(USER_FIELDS)
                print("")

            user_data["salt"] = base64.b64encode(str(uuid4()).encode()).decode()
            user_data["password"] = base64.b64encode(
                hash_value(value=user_data["password"], salt=user_data["salt"])
            ).decode()

        if self.kwargs.get("tables"):
            LOG.info("#c<Creating tables...>")
            create_all_tables(DB, safe=False)

        if self.kwargs.get("data") or self.kwargs.get("demo"):
            LOG.info("#c<Populating the database with essential data...>")

            output = {}
            with DB.atomic():
                if self.kwargs.get("force"):
                    # AuthProvider is the only entity that not cascade when the company is deleted
                    AuthProvider.delete().execute()
                    Company.delete().execute()

                company = Company.create(name="Default")
                organization = Organization.create(name="Default", company=company)
                project = Project.create(name="Default", company=company, organization=organization)
                user = User.create(primary_company=company, **user_data)
                output.update(
                    {
                        "company_id": str(company.id),
                        "organization_id": str(organization.id),
                        "project_id": str(project.id),
                        "user_id": str(user.id),
                    }
                )

                if self.kwargs.get("demo"):
                    sa_key = generate_key(
                        allowed_services=["EVENTS_API", "OBSERVABILITY_API", "AGENT_API"],
                        project=project,
                        name="Demo",
                        description="This key is utilized by the product demo",
                    )

                    action_args = {"from_address": "notify@example.com", "recipients": [], "template": "NotifyTemplate"}
                    action = Action.create(
                        name="Send Email", action_impl="SEND_EMAIL", company=company, action_args=action_args
                    )

                    output.update(
                        {
                            "action_id": str(action.id),
                            "service_account_key": sa_key.encoded_key,
                        }
                    )

            if self.kwargs.get("json"):
                json.dump(output, sys.stdout)
                sys.stdout.write("\n")
                sys.stdout.flush()
            else:
                for key, value in output.items():
                    LOG.info("    #c<%#20s>: %s", key, value)
