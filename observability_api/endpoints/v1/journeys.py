__all__ = ["Journeys", "JourneyById", "JourneyDag", "JourneyDagEdgeById"]

import logging
from graphlib import CycleError
from http import HTTPStatus
from uuid import UUID

from flask import Response, make_response, request
from peewee import DoesNotExist, IntegrityError
from werkzeug.exceptions import Conflict, NotFound

from common.api.base_view import Permission
from common.api.request_parsing import no_body_allowed
from common.entities import DB, Component, Journey, JourneyDagEdge, Project
from common.entity_services import ProjectService
from common.entity_services.helpers import ListRules, Page
from observability_api.endpoints.entity_view import BaseEntityView
from observability_api.schemas import (
    JourneyDagEdgePostSchema,
    JourneyDagEdgeSchema,
    JourneyDagSchema,
    JourneyPatchSchema,
    JourneySchema,
)

LOG = logging.getLogger(__name__)


class Journeys(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, project_id: UUID) -> Response:
        """
        Journey LIST
        ---
        tags: ["Journey"]
        description: Lists all journeys for the project using the specified project ID.
        operationId: ListJourneys
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
            description: The sort order for the journey list. The sort is applied to the list before pagination.
          - in: query
            name: search
            schema:
              type: string
            required: false
            description: Optional. A case-insensitive search query. If specified, only journey names with a partial or
                         full match to the query will be listed.
          - in: query
            name: component_id
            schema:
              type: string
              format: uuid
            required: false
            description: Optional. A component ID. If specified, only journeys in the given component will be listed.
        responses:
          200:
            description: Request successful - journey list returned.
            content:
              application/json:
                schema:
                  type: object
                  properties:
                    entities:
                      type: array
                      items:
                        $ref: '#/components/schemas/JourneySchema'
                    total:
                      type: integer
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
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
        component_id: str | None = request.args.get("component_id", None)
        page: Page = ProjectService.get_journeys_with_rules(
            str(project_id), ListRules.from_params(request.args), component_id=component_id
        )
        journeys = JourneySchema().dump(page.results, many=True)
        return make_response({"entities": journeys, "total": page.total})

    def post(self, project_id: UUID) -> Response:
        """
        Journey CREATE
        ---
        tags: ["Journey"]
        operationId: PostJourney
        description: Creates a new journey in a project using the specified name and project ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: project_id
            description: The ID of the project that the journey will be created under.
            schema:
              type: string
            required: true
        requestBody:
          description: The data required for the new journey.
          required: true
          content:
            application/json:
              schema: JourneySchema
        responses:
          201:
            description: Request successful - journey created.
            content:
              application/json:
                schema: JourneySchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Project not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          409:
            description: There is a data conflict with the information in the new journey.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        journey = self.parse_body(schema=JourneySchema())
        journey.project = self.get_entity_or_fail(Project, Project.id == project_id)
        journey.created_by = self.user
        with DB.atomic():
            try:
                journey.save(force_insert=True)
            except IntegrityError as e:
                LOG.exception("Journey CREATE failed")
                raise Conflict("Failed to create Journey; one already exists with that information") from e
        # Marshmallow passes peewee's backref query to the schema instead of the result of the query unless the result
        # is prefetched. The journey has just been created so that result would be empty
        journey.instance_rules = []
        return make_response(JourneySchema().dump(journey), HTTPStatus.CREATED)


class JourneyById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, journey_id: UUID) -> Response:
        """
        Get journey by ID
        ---
        tags: ["Journey"]
        operationId: GetJourneyById
        description: Retrieves a single journey by its ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - journey returned.
            content:
              application/json:
                schema: JourneySchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Journey not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        journey = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        # Marshmallow passes peewee's backref query to the schema instead of the result of the query unless the result
        # is prefetched.
        journey.instance_rules = list(journey.instance_rules)
        return make_response(JourneySchema().dump(journey))

    def patch(self, journey_id: UUID) -> Response:
        """
        Update journey by ID
        ---
        tags: ["Journey"]
        description: Updates attributes for a single journey. Use this request to change a journey name and description
        operationId: PatchJourneyById
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            schema:
              type: string
            required: true
        requestBody:
          description: The update data for the journey.
          required: true
          content:
            application/json:
              schema: JourneyPatchSchema
        responses:
          200:
            description: Request successful - journey updated.
            content:
              application/json:
                schema: JourneySchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Journey not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        self.parse_body(schema=JourneyPatchSchema())
        _ = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        try:
            with DB.atomic():
                Journey.update(**self.request_body).where(Journey.id == journey_id).execute()
        except IntegrityError as e:
            LOG.exception("Journey UPDATE failed")
            raise Conflict("Failed to update Journey; one already exists with that information") from e
        journey = Journey.get_by_id(journey_id)
        # Marshmallow passes peewee's backref query to the schema instead of the result of the query unless the result
        # is prefetched.
        journey.instance_rules = list(journey.instance_rules)
        return make_response(JourneySchema().dump(journey))

    @no_body_allowed
    def delete(self, journey_id: UUID) -> Response:
        """
        Delete a Journey by ID
        ---
        tags: ["Journey"]
        operationId: DeleteJourneyById
        description: Permanently deletes a single journey by its ID.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - journey deleted.
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        try:
            _ = self.get_entity_or_fail(Journey, Journey.id == journey_id)
            with DB.atomic():
                Journey.delete().where(Journey.id == journey_id).execute()
        except NotFound:
            pass
        return make_response("", HTTPStatus.NO_CONTENT)


class JourneyDag(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def get(self, journey_id: UUID) -> Response:
        """
        Get DAG by journey ID
        ---
        tags: ["Journey"]
        operationId: JourneyDag
        description: Retrieves the DAG by the ID of it's journey.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            schema:
              type: string
            required: true
        responses:
          200:
            description: Request successful - journey dag returned.
            content:
              application/json:
                schema: JourneyDagSchema
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Journey not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        journey = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        data: dict[str, list] = {"nodes": []}
        graph = journey.journey_dag
        for x in journey.dag_nodes:
            data["nodes"].append({"component": x, "edges": graph[x]})

        return make_response(JourneyDagSchema().dump(data))

    def put(self, journey_id: UUID) -> Response:
        """
        Journey DAG edge CREATE
        ---
        tags: ["JourneyDag"]
        operationId: CreateJourneyDagEdge
        description: Creates a new DAG edge for a Journey.
        security:
          - SAKey: []
        parameters:
          - in: path
            name: journey_id
            description: The ID of the Journey that the DAG edge will be created under.
            schema:
              type: string
            required: true
        requestBody:
          description: The data required for the new DAG edge.
          required: true
          content:
            application/json:
              schema: JourneyDagEdgeSchema
        responses:
          201:
            description: Request successful - DAG edge created.
            content:
              application/json:
                schema: JourneyDagEdgePostSchema
          400:
            description: There is invalid or missing data in the request body.
            content:
              application/json:
                schema: HTTPErrorSchema
          404:
            description: Project not found.
            content:
              application/json:
                schema: HTTPErrorSchema
          409:
            description: There is a data conflict with the information in the new DAG edge.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        journey = self.get_entity_or_fail(Journey, Journey.id == journey_id)
        edge_data = self.parse_body(schema=JourneyDagEdgePostSchema())

        left_id = edge_data.get("left")
        if left_id:
            try:
                left_edge = Component.get_by_id(left_id)
            except DoesNotExist as dne:
                raise NotFound(f"No Component exists with the ID '{left_id}'") from dne
        else:
            left_edge = None

        right_id = edge_data.get("right")
        if right_id:
            try:
                right_edge = Component.get_by_id(right_id)
            except DoesNotExist as dne:
                raise NotFound(f"No Component exists with the ID '{right_id}'") from dne
        else:
            right_edge = None

        dag_edge = JourneyDagEdge(journey=journey, left=left_edge, right=right_edge)

        # Validate the new edge is valid
        graph = journey.journey_dag
        Journey.add_edge_to_graph(graph=graph, edge=dag_edge)
        try:
            Journey.validate_graph(graph)
        except CycleError as ce:
            raise Conflict("Graph edge would yield an invalid graph") from ce

        try:
            dag_edge.save(force_insert=True)
        except IntegrityError as ie:
            raise Conflict("A Journey DAG edge must be unique") from ie
        return make_response(JourneyDagEdgeSchema().dump(dag_edge), HTTPStatus.CREATED)


class JourneyDagEdgeById(BaseEntityView):
    PERMISSION_REQUIREMENTS: tuple[Permission, ...] = ()

    @no_body_allowed
    def delete(self, edge_id: UUID) -> Response:
        """
        Delete a DAG edge by ID
        ---
        tags: ["JourneyDag"]
        description: Permanently deletes a single user by its ID.
        operationId: DeleteDagEdgeById
        security:
          - SAKey: []
        parameters:
          - in: path
            name: edge_id
            schema:
              type: string
            required: true
        responses:
          204:
            description: Request successful - DAG edge deleted.
          400:
            description: Request bodies are not supported by this endpoint.
            content:
              application/json:
                schema: HTTPErrorSchema
          500:
            description: Unverified error. Consult the response body for more details.
            content:
              application/json:
                schema: HTTPErrorSchema

        """
        try:
            dag_edge = self.get_entity_or_fail(JourneyDagEdge, JourneyDagEdge.id == edge_id)
        except NotFound:
            pass
        else:
            dag_edge.delete_instance()
        return make_response("", HTTPStatus.NO_CONTENT)
