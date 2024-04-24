import logging
from typing import Any, Optional

from apispec import BasePlugin

from observability_api.routes.v1_routes import SUBCOMPONENT_BY_ID_VIEWS, SUBCOMPONENTS_VIEWS

LOG = logging.getLogger(__name__)


class SubcomponentPlugin(BasePlugin):
    subcomponent_name: str
    response_schema: str
    request_schema: str

    def operation_helper(
        self,
        path: Optional[str] = None,
        operations: Optional[dict] = None,
        **kwargs: Any,
    ) -> None:
        description_dict: dict[str, str] = {
            "get": "Retrieves a single [SUBCOMPONENT] component by ID.",
            "patch": "Updates attributes of a single [SUBCOMPONENT] component.",
            "post": "Creates a new [SUBCOMPONENT] component in the specified project.",
        }

        view = kwargs["view"].view_class
        if view.__name__ in [v.__name__ for v in [*SUBCOMPONENTS_VIEWS, *SUBCOMPONENT_BY_ID_VIEWS]]:
            if operations is None:
                operations = {}
            for method, value in operations.items():
                self.subcomponent_name = view.route[:-1]
                self.response_schema = view.schema.__name__

                value["tags"] = [self.subcomponent_name.title()]
                value["operationId"] = f"{method.title()}{view.__name__}"
                value["description"] = description_dict.get(method, "").replace(
                    "[SUBCOMPONENT]", self.subcomponent_name
                )
                value["security"] = [{"SAKey": []}]
                value["parameters"] = [self.parameter_helper(method=method, subcomponent_name=self.subcomponent_name)]
                if method in ("post", "patch"):
                    self.request_schema = view.patch_schema.__name__ if method == "patch" else self.response_schema
                    value["requestBody"] = self.request_body_helper(method=method)
                value["responses"] = self.response_helper(method=method)

    def request_body_helper(self, method: str) -> dict:
        request_body_desc_dict: dict[str, str] = {
            "patch": "The update data for the [SUBCOMPONENT] component.",
            "post": "The data required for the new [SUBCOMPONENT] component.",
        }
        content = {"application/json": {"schema": self.request_schema}}
        request_body = {
            "description": request_body_desc_dict.get(method, "").replace("[SUBCOMPONENT]", self.subcomponent_name),
            "required": True,
            "content": content,
        }
        return request_body

    def parameter_helper(self, parameter: Optional[dict] = None, **kwargs: Any) -> dict:
        method = kwargs["method"]
        parameter = {"in": "path", "schema": {"type": "string"}, "required": "true", "name": "component_id"}
        if method == "post":
            parameter["name"] = "project_id"
            parameter["description"] = f"The ID of the project that the {self.subcomponent_name} will be created under."
        return parameter

    def response_helper(self, response: Optional[dict] = None, **kwargs: Any) -> dict:
        method = kwargs["method"]
        response_desc_dict: dict[str, dict[int, str]] = {
            "get": {
                200: f"Request successful - {self.subcomponent_name} component returned.",
                400: "Request bodies are not supported by this endpoint.",
                404: f"{self.subcomponent_name} not found.",
            },
            "patch": {
                200: f"Request successful - {self.subcomponent_name} component updated.",
                400: "There is invalid or missing data in the request body.",
                404: f"{self.subcomponent_name} not found.",
            },
            "post": {
                200: "",
                400: "There is invalid or missing data in the request body.",
                404: "Project not found.",
            },
        }

        response = {
            200: {
                "description": response_desc_dict[method][200],
                "content": {"application/json": {"schema": self.response_schema}},
            },
            201: {
                "description": f"Request successful - {self.subcomponent_name} component created.",
                "content": {"application/json": {"schema": self.response_schema}},
            },
            400: {
                "description": response_desc_dict[method][400],
                "content": {"application/json": {"schema": "HTTPErrorSchema"}},
            },
            404: {
                "description": response_desc_dict[method][404],
                "content": {"application/json": {"schema": "HTTPErrorSchema"}},
            },
            409: {
                "description": f"There is a data conflict with the new {self.subcomponent_name} component information.",
                "content": {"application/json": {"schema": "HTTPErrorSchema"}},
            },
            500: {
                "description": "Unverified error. Consult the response body for more details.",
                "content": {"application/json": {"schema": "HTTPErrorSchema"}},
            },
        }
        if method == "post":
            del response[200]
        else:
            del response[201]
            del response[409]
        return response
