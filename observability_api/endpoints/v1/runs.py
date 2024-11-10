__all__ = ["Runs", "RunById"]

import logging
from uuid import UUID

from flask import Response, make_response, request
from peewee import PREFETCH_TYPE, fn
from werkzeug.exceptions import NotFound

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import Pipeline, Project, Run, RunAlert, RunTask, TestOutcome
from common.entity_services import ProjectService
from common.entity_services.helpers import ListRules, Page, RunFilters
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas.run_schemas import RunSchema

LOG = logging.getLogger(__name__)


class Runs(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Run LIST
        ---
        tags: ["Run"]
        description: List all runs in a pipeline.
        operationId: ListRuns
        security:
          - SAKey: []

        Parameters
        ----------
          - in: path
            name: project_id
            description: the ID of the project being queried.
            schema:
              type: string
              format: uuid
            required: true
          - in: query
            name: status
            description: Optional. If specified, the results will be limited to run with one of the specified statuses.
            schema:
              type: array
              items:
                type: string
          - in: query
            name: pipeline_id
            description: Optional. Specifies which pipelines to include by their ID. All pipelines are selected if
                         unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
            schema:
              type: boolean
            required: false
          - in: query
            name: start_range_begin
            description: Optional. An ISO8601 datetime. If specified, The result will only include runs with a
                         start_time field equal or past the given datetime. May be specified with start_range_end
                         to create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: start_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only contain runs with a
                         start_time field before the given datetime. May be specified with start_range_begin to create
                         a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_begin
            description: Optional. An ISO8601 datetime. If specified, The result will only include runs with an
                         end_time field equal or past the given datetime. May be specified with end_range_end to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_end
            description: Optional. An ISO8601 datetime. If specified, The result will only include runs with an
                         end_time field before the given datetime. May be specified with end_range_begin to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: pipeline_key
            description: Optional. If specified, the results will be limited to runs with the pipeline keys.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: run_key
            description: Optional. If specified, the results will be limited to runs with one of the listed keys.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: instance_id
            description: Optional. If specified, the results will be limited to runs with one of the listed instance ids.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: tool
            description: Optional. If specified, the results will be limited to runs using the listed tools.
            schema:
              type: array
              items:
                type: string
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
            description:  The sort order for the run list. The sort is applied to the list before pagination.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, runs with keys or
                         names that have a partial or full match to the query will be listed.
        responses:
          200:
            description: Request successful - Run list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/RunSchema'
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
        _ = self.get_entity_or_fail(Project, Project.id == project_id)
        pipeline_ids: list[str] = request.args.getlist("pipeline_id")
        page: Page = ProjectService.get_runs_with_rules(
            str(project_id),
            pipeline_ids,
            ListRules.from_params(request.args),
            RunFilters.from_params(request.args),
        )
        runs = RunSchema().dump(page.results, many=True)
        return make_response({"entities": runs, "total": page.total})


class RunById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, run_id: UUID) -> Response:
        """
        Get Run by ID
        ---
        tags: ["Run"]
        description: Retrieves the details of a single run by its ID.
        security:
          - SAKey: []
        operationId: GetRunById
        parameters:
          - in: path
            name: run_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - run details returned.
            content:
              application/json:
                schema: RunSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
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

        try:
            tasks_summary = RunTask.select(RunTask.run, RunTask.status, fn.COUNT(RunTask.id).alias("count")).group_by(
                RunTask.status
            )
            alerts = RunAlert.select(RunAlert).join(Run).where(RunAlert.run == run_id)
            # The below is a single element list as a result of the prefetch, thus the pop. Does not refer to the
            # peewee function.
            tests_summary = TestOutcome.select(
                TestOutcome.run, TestOutcome.status, fn.COUNT(TestOutcome.id).alias("count")
            ).group_by(TestOutcome.run, TestOutcome.status)
            run: Run = (
                Run.select(Run, Pipeline)
                .join(Pipeline)
                .where(Run.id == run_id)
                .prefetch(tasks_summary, alerts, tests_summary, prefetch_type=PREFETCH_TYPE.JOIN)
            ).pop()
        except IndexError as ie:
            LOG.info("No run exists with the following ID: '%s'", run_id)
            raise NotFound(f"No run exists with the following ID: '{run_id}") from ie
        return make_response(RunSchema().dump(run))
