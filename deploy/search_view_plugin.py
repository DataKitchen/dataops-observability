import logging
from typing import Any

from apispec import BasePlugin
from apispec.yaml_utils import load_yaml_from_docstring

from common.api.search_view import SearchView

LOG = logging.getLogger(__name__)


class SearchViewPlugin(BasePlugin):
    """
    Generates SearchView's docs based on the related GET endpoint docs.
    """

    def operation_helper(
        self,
        path: str | None = None,
        operations: dict | None = None,
        **kwargs: Any,
    ) -> None:
        view_class = getattr(kwargs.get("view", None), "view_class", None)
        if operations and view_class and issubclass(view_class, SearchView):
            spec = load_yaml_from_docstring(view_class.get.__doc__)
            schema_properties = {}
            for parameter in spec.get("parameters", []).copy():
                if parameter.get("in", "").lower() == "query":
                    param_type = parameter.get("schema", {}).get("type")
                    match param_type:
                        case "array":
                            body_param = {
                                "description": parameter.get("description", None),
                                "type": param_type,
                                "items": parameter["schema"].get("items"),
                            }
                        case None:
                            raise Exception(f"Cannot handle parameter: {parameter}")
                        case _:
                            body_param = parameter["schema"]
                            body_param["description"] = parameter.get("description", None)

                    schema_properties[parameter["name"]] = body_param
                    spec["parameters"].remove(parameter)

            params_payload = {"type": "object", "properties": schema_properties}
            spec["requestBody"] = {
                "description": "Search parameters payload",
                "required": True,
                "content": {
                    "application/json": {"schema": {"type": "object", "properties": {"params": params_payload}}}
                },
            }

            spec["tags"] = ["Search"]
            spec["operationId"] = f"{spec['operationId']}Search"

            operations["post"].update(spec)
