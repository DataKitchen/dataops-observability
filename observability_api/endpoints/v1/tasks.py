__all__ = ["RunTasks"]

import logging
from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Run
from common.entity_services import RunService
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import RunTaskSchema

LOG = logging.getLogger(__name__)


class RunTasks(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, run_id: UUID) -> Response:
        """
        Run LIST
        ---
        tags: ["Task"]
        description: List all RunTasks in a Run.
        operationId: ListRunTasks
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: run_id
            description: the ID of the run being queried.
            schema:
              type: string
              format: uuid
            required: true
          - in: query
            name: sort
            schema:
              type: string
              default: ASC
              enum:
                - ASC
                - DESC
            description: The sort order for the task run list. Sorting is done on start_time.
        responses:
          200:
            description: Request successful - RunTasks list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/RunTaskSchema'
                    total:
                      type: integer
          404:
            description: Run not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        _ = self.get_entity_or_fail(Run, Run.id == run_id)
        page: Page = RunService.get_runtasks_with_rules(run_id, ListRules.from_params(request.args))
        runs = RunTaskSchema().dump(page.results, many=True)
        return make_response({"entities": runs, "total": page.total})
