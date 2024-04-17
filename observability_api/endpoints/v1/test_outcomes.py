from uuid import UUID

from flask import Response, make_response, request

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Project, TestOutcome
from common.entity_services import ProjectService
from common.entity_services.helpers import ListRules, Page, TestOutcomeItemFilters
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import TestOutcomeItemSchema


class ProjectTests(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """Project test outcomes LIST
        ---

        tags: ["TestOutcome"]
        description: List all test outcomes in a project.
        operationId: ListProjectTestOutcomes
        security:
          - SAKey: []
        parameters:
          - in: path
            name: project_id
            description: the ID of the project being queried.
            schema:
              type: string
            required: true
          - in: query
            name: component_id
            description: Optional. If specified, the results will be limited to test outcomes that belong to one of the
                         given component IDs.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: status
            description: Optional. If specified, the results will be limited to test outcomes that have to one of the
                         given statuses.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: start_range_begin
            description: Optional. An ISO8601 datetime. If specified, the result will only include test outcomes with a
                         start_time field equal or past the given datetime. May be specified with start_range_end
                         to create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: start_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only contain test outcomes with a
                         start_time field before the given datetime. May be specified with start_range_begin to create
                         a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_begin
            description: Optional. An ISO8601 datetime. If specified, the result will only include test outcomes with an
                         end_time field equal or past the given datetime. May be specified with end_range_end to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only include test outcomes with an
                         end_time field before the given datetime. May be specified with end_range_begin to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: instance_id
            description: Optional. The ID of the Instance to filter against. If specified, the result will only include
                         test outcomes related to the given Instance.
            schema:
              type: string
              format: uuid
            required: false
          - in: query
            name: run_id
            description: Optional. The ID of the Run to filter against. If specified, the result will only include
                         test outcomes related to the given Run.
            schema:
              type: string
              format: uuid
            required: false
          - in: query
            name: page
            schema:
              type: integer
              default: 1
            description: A page number to use for pagination. All pagination starts with 1.
          - in: query
            name: count
            schema:
              type: integer
              default: 10
            description: The number of results to display per page.
          - in: query
            name: sort
            schema:
              type: string
              default: ASC
              enum:
                - ASC
                - DESC
            description:  The sort order for the test outcomes list.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, test outcomes with names or
                         descriptions that have a partial or full match to the query will be listed.
          - in: query
            name: key
            description: Optional. The key of the TestOutcome to filter against. If specified, the result will only
                         include test outcomes which share the same key value.
            schema:
              type: string
              format: uuid
        responses:
          200:
            description: Request successful - List of test outcomes returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/TestOutcomeItemSchema'
                    total:
                      type: integer
          404:
            description: Project not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        project = self.get_entity_or_fail(Project, Project.id == project_id)
        page: Page = ProjectService.get_test_outcomes_with_rules(
            project,
            ListRules.from_params(request.args),
            TestOutcomeItemFilters.from_params(request.args),
        )
        return make_response({"entities": TestOutcomeItemSchema().dump(page.results, many=True), "total": page.total})


class TestOutcomeById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, test_outcome_id: UUID) -> Response:
        """Get TestOutcome by ID
        ---
        tags: ["TestOutcome"]
        operationId: GetTestOutcomeById
        description: Retrieves a single test outcome by its ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: test_outcome_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - test outcome returned.
            content:
              application/json:
                schema: TestOutcomeItemSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Test outcome not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        test_outcome = self.get_entity_or_fail(TestOutcome, TestOutcome.id == test_outcome_id)
        return make_response(TestOutcomeItemSchema().dump(test_outcome))
