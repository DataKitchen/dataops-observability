from collections import defaultdict
from dataclasses import dataclass
from graphlib import CycleError
from typing import Optional

import pytest

from common.entities import Journey


@dataclass
class FakeEdge:
    left: Optional[str]
    right: str

    def __hash__(self):
        return hash((self.left, self.right))

    def __eq__(self, other):
        return self.left == self.left and self.right == self.right


@pytest.mark.unit
def test_validate_invalid_graph():
    """An CycleError should be raised when given a graph with cycles."""
    invalid_graph = {
        "a": {FakeEdge(right="a", left="b"), FakeEdge(right="a", left="c")},
        "b": {FakeEdge(right="b", left="d")},
        "d": {FakeEdge(right="d", left="a")},
    }
    with pytest.raises(CycleError):
        Journey.validate_graph(invalid_graph)


@pytest.mark.unit
def test_validate_graph():
    """An CycleError should be raised when given a graph with cycles."""
    graph = {"a": {FakeEdge(right="a", left="b"), FakeEdge(right="a", left="c")}, "b": {FakeEdge(right="b", left="d")}}
    try:
        Journey.validate_graph(graph)
    except CycleError:
        raise AssertionError(f"Graph should have passed validation: {graph}")


@pytest.mark.unit
def test_add_edge_to_graph_left_and_right():
    graph = defaultdict(set)
    graph["a"] = {"b", "c"}
    graph["b"] = {"d"}
    edge = FakeEdge(left="d", right="e")
    Journey.add_edge_to_graph(graph=graph, edge=edge)
    expected = {"a": {"c", "b"}, "b": {"d"}, "e": edge}
    assert expected == graph, "Edge not appropriately added to graph"


@pytest.mark.unit
def test_add_edge_to_graph_right_only():
    graph = defaultdict(set)
    graph["a"] = {"b", "c"}
    graph["b"] = {"d"}
    edge = FakeEdge(right="z", left=None)
    Journey.add_edge_to_graph(graph=graph, edge=edge)
    expected = {"a": {"c", "b"}, "b": {"d"}, "z": edge}
    assert expected == graph, "Edge not appropriately added to graph"


@pytest.mark.unit
def test_add_edge_to_graph_left_only():
    """Attempting to add an edge with only a left side raises a ValueError."""
    graph = defaultdict(set)
    graph["a"] = {"b", "c"}
    graph["b"] = {"d"}
    edge = FakeEdge(left="z", right=None)
    with pytest.raises(ValueError):
        Journey.add_edge_to_graph(graph=graph, edge=edge)


@pytest.mark.unit
def test_add_edge_to_graph_no_relationships():
    """Attempting to add an edge without any relationship raises a ValueError."""
    graph = defaultdict(set)
    graph["a"] = {"b", "c"}
    graph["b"] = {"d"}
    edge = FakeEdge(left=None, right=None)
    with pytest.raises(ValueError):
        Journey.add_edge_to_graph(graph=graph, edge=edge)
