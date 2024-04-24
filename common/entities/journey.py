from __future__ import annotations

__all__ = ["JourneyDagEdge", "Journey"]

from collections import defaultdict
from graphlib import CycleError, TopologicalSorter
from typing import DefaultDict

from peewee import CharField, ForeignKeyField

from .base_entity import AuditEntityMixin, AuditUpdateTimeEntityMixin, BaseEntity
from .component import Component
from .project import Project


class Journey(BaseEntity, AuditEntityMixin, AuditUpdateTimeEntityMixin):
    """Representation of a Journey for the application."""

    name = CharField(unique=False, null=True)
    description = CharField(null=True)
    project = ForeignKeyField(Project, backref="journeys", on_delete="CASCADE", null=False, index=True)

    @staticmethod
    def add_edge_to_graph(*, graph: DefaultDict[JourneyDagEdge, set[JourneyDagEdge]], edge: JourneyDagEdge) -> None:
        if edge.right:
            graph[edge.right].add(edge)
        else:
            raise ValueError(f"Graph edge must have a right edge; left: {edge.left} - right: {edge.right}")

    @staticmethod
    def validate_graph(graph: DefaultDict[JourneyDagEdge, set[JourneyDagEdge]]) -> None:
        ts = TopologicalSorter({n: [o.left for o in m if o.left] for n, m in graph.items()})
        ts.prepare()  # Will raise a CycleError if there are cycles in the graph

    @property
    def journey_dag(self) -> DefaultDict[Component, set[JourneyDagEdge]]:
        """Return a graph of Components."""
        graph: DefaultDict[Component, set[JourneyDagEdge]] = defaultdict(set)
        for edge in self.dag_edges:
            self.add_edge_to_graph(graph=graph, edge=edge)

        # Validate the graph has no cycles
        try:
            self.validate_graph(graph)
        except CycleError as e:
            raise ValueError("Journey DAG contains cycle errors") from e

        return graph

    @property
    def dag_nodes(self) -> list[Component]:
        qobj = (JourneyDagEdge.left == Component.id) | (JourneyDagEdge.right == Component.id)
        qs = Component.select().join(JourneyDagEdge, on=qobj).where(JourneyDagEdge.journey == self).distinct()
        return list(qs)

    class Meta:
        indexes = ((("name", "project"), True),)


class JourneyDagEdge(BaseEntity, AuditUpdateTimeEntityMixin):
    """Represents an edge relationship between two components in a DAG."""

    journey = ForeignKeyField(Journey, backref="dag_edges", on_delete="CASCADE", null=False, index=True)

    left = ForeignKeyField(Component, backref="left_dag_edges", on_delete="CASCADE", null=True, index=True)
    right = ForeignKeyField(Component, backref="right_dag_edges", on_delete="CASCADE", null=False, index=True)

    class Meta:
        table_name = "journey_dag_edge"
        indexes = ((("journey_id", "left_id", "right_id"), True),)
