import logging
from typing import Type
from uuid import UUID

from flask import Response, make_response, request
from marshmallow import Schema
from werkzeug.exceptions import Forbidden

from common.api.base_view import PERM_USER, Permission, SearchableView
from common.api.request_parsing import no_body_allowed
from common.entities import Component, Instance, InstanceRule, Journey, Project, Schedule
from common.entity_services import InstanceService, ProjectService, UpcomingInstanceService
from common.entity_services.helpers import Filters, ListRules, Page
from common.entity_services.helpers.filter_rules import PROJECT_ID_QUERY_NAME
from common.entity_services.instance_dag_service import InstanceDagService
from common.schemas.filter_schemas import CompanyInstanceFiltersSchema, InstanceFiltersSchema
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas.instance_schemas import InstanceDetailedSchema
from observability_api.schemas.instance_dag_schemas import InstanceDagSchema


LOG = logging.getLogger(__name__)


class Instances(BaseEntityView, SearchableView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()
    FILTERS_SCHEMA: Type[Schema] = InstanceFiltersSchema

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """Instance LIST
        ---
        tags: ["Instance"]
        description: List all instances of a journey.
        operationId: ListInstances
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
            name: journey_id
            description: Optional. Specifies which journeys to include by their ID. All journeys are selected if
                         unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: active
            description: Optional. When true, instances without a reported end_time are returned i.e., uncompleted
                         instances. When active is false, instances with a reported end_time are returned i.e.,
                         completed instances. Leave this query unspecified to return instances with both states. Cannot
                         be specified with end_range_begin or end_range_end.
            schema:
              type: boolean
            required: false
          - in: query
            name: start_range_begin
            description: Optional. An ISO8601 datetime. If specified, The result will only include instances with a
                         start_time field equal or past the given datetime. May be specified with start_range_end
                         to create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: start_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only contain instances with a
                         start_time field before the given datetime. May be specified with start_range_begin to create
                         a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_begin
            description: Optional. An ISO8601 datetime. If specified, The result will only include instances with an
                         end_time field equal or past the given datetime. May be specified with end_range_end to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_end
            description: Optional. An ISO8601 datetime. If specified, The result will only include instances with an
                         end_time field before the given datetime. May be specified with end_range_begin to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: journey_name
            description: Optional. If specified, the results will be limited to instances with the journeys named.
            schema:
              type: array
              items:
                type: string
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
            description:  The sort order for the instance list.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only instances with payload key value
                         that is a partial or full match to the query will be listed.
        responses:
          200:
            description: Request successful - Instance list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/InstanceDetailedSchema'
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
        page: Page[Instance] = ProjectService.get_instances_with_rules(
            ListRules.from_params(self.args),
            Filters.from_dict(self.FILTERS_SCHEMA().load(self.args)),
            [str(project_id)],
        )
        return make_response({"entities": InstanceDetailedSchema().dump(page.results, many=True), "total": page.total})


class CompanyInstances(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = (PERM_USER,)
    FILTERS_SCHEMA: Type[Schema] = CompanyInstanceFiltersSchema

    @no_body_allowed
    def get(self) -> Response:
        """Instance LIST at company level
        ---
        tags: ["Instance"]
        description: List all instances in the company.
        operationId: ListCompanyInstances
        security:
          - SAKey: []
        parameters:
          - in: query
            name: project_id
            description: Optional. Specifies the project IDs to include. All projects are selected if unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: journey_id
            description: Optional. Specifies which journeys to include by their ID. All journeys are selected if
                         unset.
            schema:
              type: array
              items:
                type: string
                format: uuid
            required: false
          - in: query
            name: active
            description: Optional. When true, instances without a reported end_time are returned i.e., uncompleted
                         instances. When active is false, instances with a reported end_time are returned i.e.,
                         completed instances. Leave this query unspecified to return instances with both states. Cannot
                         be specified with end_range_begin or end_range_end.
            schema:
              type: boolean
            required: false
          - in: query
            name: start_range_begin
            description: Optional. An ISO8601 datetime. If specified, The result will only include instances with a
                         start_time field equal or past the given datetime. May be specified with start_range_end
                         to create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: start_range_end
            description: Optional. An ISO8601 datetime. If specified, the result will only contain instances with a
                         start_time field before the given datetime. May be specified with start_range_begin to create
                         a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_begin
            description: Optional. An ISO8601 datetime. If specified, The result will only include instances with an
                         end_time field equal or past the given datetime. May be specified with end_range_end to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: end_range_end
            description: Optional. An ISO8601 datetime. If specified, The result will only include instances with an
                         end_time field before the given datetime. May be specified with end_range_begin to
                         create a range.
            schema:
              type: string
              format: date
            required: false
          - in: query
            name: journey_name
            description: Optional. If specified, the results will be limited to instances with the journeys named.
            schema:
              type: array
              items:
                type: string
            required: false
          - in: query
            name: status
            description: Optional. If specified, the results will be limited to instances with the specified statuses.
            schema:
              type: array
              items:
                type: string
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
            description:  The sort order for the instance list.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only instances with payload key value
                         that is a partial or full match to the query will be listed.
        responses:
          200:
            description: Request successful - Instance list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/InstanceDetailedSchema'
                    total:
                      type: integer
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        if not self.user:
            raise Forbidden()
        project_ids = request.args.getlist(PROJECT_ID_QUERY_NAME)
        company_id = str(self.user.primary_company.id)
        page: Page[Instance] = ProjectService.get_instances_with_rules(
            ListRules.from_params(request.args),
            Filters.from_dict(self.FILTERS_SCHEMA().load(self.args)),
            project_ids,
            company_id,
        )
        return make_response({"entities": InstanceDetailedSchema().dump(page.results, many=True), "total": page.total})


class InstanceById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, instance_id: UUID) -> Response:
        """Get instance by ID
        ---
        tags: ["Instance"]
        operationId: GetInstanceById
        description: Retrieves a single instance by its ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: instance_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - instance returned.
            content:
              application/json:
                schema: InstanceDetailedSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Instance not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        result: Instance = self.get_entity_from_query_or_fail(
            Instance.select(Instance, Journey, Project).where(Instance.id == instance_id)
        )
        if result.active:
            result.journey.instance_rules = (
                InstanceRule.select().where(InstanceRule.journey == result.journey).prefetch(Component, Schedule)
            )
            if upcoming := next(
                UpcomingInstanceService.get_upcoming_instances(result.journey, result.start_time), None
            ):
                result.expected_end_time = upcoming.expected_start_time or upcoming.expected_end_time
        InstanceService.aggregate_runs_summary([result])
        InstanceService.aggregate_tests_summary([result])
        InstanceService.aggregate_alerts_summary([result])
        return make_response(InstanceDetailedSchema().dump(result))


class InstanceDag(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, instance_id: UUID) -> Response:
        """Get DAG by instance ID
        --
        tags: ["Instance"]
        operationId: GetInstanceDag
        description: Retrieves the DAG of an instance.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: instance_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - instance returned.
            content:
              application/json:
                schema: InstanceDetailedSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Instance not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema
        """
        instance: Instance = self.get_entity_from_query_or_fail(
            Instance.select(Instance, Journey).where(Instance.id == instance_id)
        )
        return InstanceDagSchema().dump(InstanceDagService.get_nodes_with_summaries(instance))
