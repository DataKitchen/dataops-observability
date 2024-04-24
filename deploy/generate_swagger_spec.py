#!/usr/bin/env python3
"""
This script is used to generate the YAML file that we need for Swagger docs. Is used by the build system to
create the artifact necessary to render the HTML documentation.

WARNING: If you're working on this file locally, note that it pulls the Schemas from your last pip install of the
         project. So when testing with new schemas, run `pip install . && ./deploy/generate_swagger_spec.py`
"""
import logging
import sys
from itertools import chain
from pathlib import Path
from typing import Callable, Collection, Iterable, Union

from apispec import APISpec
from apispec.ext.marshmallow import MarshmallowPlugin
from apispec_webframeworks.flask import FlaskPlugin
from flask import Flask
from search_view_plugin import SearchViewPlugin
from subcomponent_plugin import SubcomponentPlugin

from common.api.flask_ext.authentication import ServiceAccountAuth
from common.events.v1 import ALL_API_EVENT_SCHEMAS, ALL_EVENT_SCHEMAS
from common.events.v2 import ALL_API_EVENT_SCHEMAS as ALL_API_EVENT_SCHEMAS_V2
from event_api.config.defaults import API_PREFIX as EVENTS_PREFIX
from event_api.routes import build_v1_routes as event_routes_v1
from event_api.routes import build_v2_routes as event_routes_v2
from observability_api.config.defaults import API_PREFIX as OBSERVE_PREFIX
from observability_api.routes import build_v1_routes as observability_routes
from observability_api.schemas import ALL_SCHEMAS

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)
LOG.addHandler(logging.StreamHandler(sys.stdout))

SA_KEY_MODEL: dict[str, str] = {
    "type": "apiKey",
    "in": "header",
    "name": ServiceAccountAuth.header_name,
    "description": "DataKitchen Observability service account key.",
}
"""The Service Account key."""

BASIC_AUTH_MODEL: dict[str, str] = {
    "type": "http",
    "scheme": "basic",
    "description": "Basic authentication.",
}

# The version of OpenAPI spec we are targeting.
# see: https://github.com/OAI/OpenAPI-Specification/releases
# For supported versions of the spec,
# see: https://apispec.readthedocs.io/en/latest/changelog.html
OPEN_API_VERSION = "3.0.2"


# see: https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.0.3.md#infoObject
OBSERVABILITY_INFO = {
    "title": "DataOps Observability Platform API",
    "description": (
        "The DataOps Observability Platform API.\n\n"
        "WARNING: This is an internal API and is subject to unannounced breaking changes."
    ),
    "license": {"name": "Proprietary, All rights reserved.", "url": "https://datakitchen.io/terms-of-service/"},
    "contact": {"name": "DataKitchen", "url": "https://datakitchen.io"},
    "version": "1.0.0",
}

EVENT_API_INFO: dict[str, Union[str, Collection]] = {
    "title": "Event Ingestion API",
    "description": "Event Ingestion API client for DataKitchen’s DataOps Observability",
    "license": {"name": "Proprietary, All rights reserved.", "url": "https://datakitchen.io/terms-of-service/"},
    "contact": {"name": "DataKitchen", "url": "https://datakitchen.io"},
}
EVENT_API_INFO_V1: dict[str, Union[str, Collection]] = {
    **EVENT_API_INFO,
    "version": "1.0.0",
}

EVENT_API_INFO_V2: dict[str, Union[str, Collection]] = {
    **EVENT_API_INFO,
    "version": "2.0.0",
}

SERVERS_INFO = [
    {
        "url": "https://datakitchen.io",
        "description": "The DataKitchen Observability Platform API server.",
    }
]


def generate_api_spec_document(
    api_information: dict[str, Union[str, Collection]],
    models: Iterable,
    api_prefix: str,
    filename: Path,
    routes: Callable,
) -> None:
    # see: https://apispec.readthedocs.io/en/latest/api_core.html#apispec.APISpec
    spec = APISpec(
        title=str(api_information["title"]),
        version=str(api_information["version"]),
        openapi_version=OPEN_API_VERSION,
        security=[{"SAKey": []}] if "Events" in api_information["title"] else [{"SAKey": []}, {"Basic": []}],
        servers=SERVERS_INFO,
        info=api_information,
        plugins=[
            MarshmallowPlugin(),
            FlaskPlugin(),
            SubcomponentPlugin(),
            SearchViewPlugin(),
        ],
    )
    for model in models:
        spec.components.schema(component_id=model.__name__, schema=model)

    # Add schemas for some basic error responses
    spec.components.schema(
        "HTTPErrorSchema",
        {
            "properties": {
                "error": {"type": "string"},
                "error_id": {"type": "string", "format": "uuid"},
                "details": {"type": "object"},
            },
            "example": {"error": "An error message.", "details": {"key": "value"}},
        },
    )
    # This will add API Key definitions to the headers, if they're defined in the spec's 'security'.
    spec.components.security_scheme("SAKey", SA_KEY_MODEL)
    spec.components.security_scheme("Basic", BASIC_AUTH_MODEL)

    app = Flask(__name__)
    views = routes(app=app, prefix=api_prefix)

    with app.test_request_context():
        for view in views:
            spec.path(view=view)

    # Create a YAML spec for all routes/schemas to be used as an artifact in builds
    # NOTE: THE FILE IS GIT-IGNORED.
    LOG.info("Generating '%s'...", filename)
    with filename.open("+w") as specfile:
        specfile.write(spec.to_yaml())


if __name__ == "__main__":
    LOG.info("Generating YAML OpenAPI Documentation.")
    generate_api_spec_document(
        OBSERVABILITY_INFO,
        chain(ALL_SCHEMAS, ALL_EVENT_SCHEMAS),
        OBSERVE_PREFIX,
        Path("observability_swagger_spec.yaml"),
        observability_routes,
    )
    generate_api_spec_document(
        EVENT_API_INFO_V1,
        ALL_API_EVENT_SCHEMAS,
        EVENTS_PREFIX,
        Path("events_swagger_spec_v1.yaml"),
        event_routes_v1,
    )
    generate_api_spec_document(
        EVENT_API_INFO_V2,
        ALL_API_EVENT_SCHEMAS_V2,
        EVENTS_PREFIX,
        Path("events_swagger_spec_v2.yaml"),
        event_routes_v2,
    )
    sys.exit(0)
