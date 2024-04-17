from array import array
from collections import OrderedDict
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal
from io import BytesIO
from pathlib import Path, PurePath, PurePosixPath, PureWindowsPath
from types import MappingProxyType
from uuid import NAMESPACE_URL, uuid1, uuid3, uuid4, uuid5

import pytest

from common.decorators import cached_property
from common.entities import RunStatus
from common.events import EventV2
from common.events.v2.batch_pipeline_status import BatchPipelineStatus
from common.events.v2.component_data import BatchPipelineData
from common.events.v2.message_log import MessageLog
from common.events.v2.metric_log import MetricLog
from common.events.v2.test_outcomes import TestGenComponentData, TestOutcomeItem, TestOutcomes, TestStatus
from common.messagepack import dump, dumps, load, loads
from testlib.fixtures.v2_events import message_log_event_v2, metric_log_event_v2  # noqa: F401


@dataclass
class SimpleDataclass:
    a: int
    b: str

    @property
    def sum(self) -> int:
        return self.a + self.b

    @cached_property
    def mean(self) -> float:
        base = self.a * self.b
        average = base / 2.0
        return average


@dataclass(slots=True)
class SlotsDataclass:
    a: int
    b: str


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    (
        Decimal("0.42"),
        Decimal("3.42"),
        Decimal("1.0"),
        Decimal("1"),
    ),
)
def test_dump_load_decimal(data):
    """Messagepack can dump/load Decimal values."""
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    (
        Path("/foo/bar.test"),
        PurePath("/foo/bar.test"),
        PurePosixPath("/foo/bar.test"),
        PureWindowsPath("c:\\foo\\bar.test"),
    ),
)
def test_dump_load_pathlib(data):
    """Messagepack can dump/load pathlib objects."""
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    (
        slice(1, 2, 3),
        slice(1, 2),
        slice(1),
        slice(1, None, 1),
    ),
)
def test_dump_load_slice(data):
    """Messagepack can dump/load slice values."""
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    (
        range(1, 2, 3),
        range(1, 2),
        range(1),
    ),
)
def test_dump_load_range(data):
    """Messagepack can dump/load range values."""
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
@pytest.mark.parametrize(
    "data",
    (
        array("b", [1, 2, 3]),
        array("B", [1, 2, 3]),
        array("i", [1, 2, 3]),
        array("I", [1, 2, 3]),
        array("h", [1, 2, 3]),
        array("H", [1, 2, 3]),
        array("l", [1, 2, 3]),
        array("L", [1, 2, 3]),
        array("q", [1, 2, 3]),
        array("Q", [1, 2, 3]),
        array("f", [1.0, 2.1, 3.0]),
        array("d", [1.0, 2.1, 3.0]),
        array("u", ["a", "b", "c"]),
    ),
)
def test_dump_load_array(data):
    """Messagepack can dump/load array values."""
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_date():
    """Messagepack can dump/load datetime.date values."""
    data = datetime.now().date()
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_time():
    """Messagepack can dump/load datetime.time values."""
    data = datetime.now().time()
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_datetime():
    """Messagepack can dump/load datetime.datetime values."""
    data = datetime.now()
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_datetime_tzinfo():
    """Messagepack can dump/load datetime.datetime values and preserve tzinfo."""
    data = datetime.now(timezone.utc)
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_mapping_proxy():
    """Messagepack can dump/load MappingProxy values."""
    data = MappingProxyType({"a": 1, "b": 2})
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_uuid1():
    """Messagepack can dump/load UUID1 values."""
    data = uuid1()
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_uuid3():
    """Messagepack can dump/load UUID3 values."""
    data = uuid3(NAMESPACE_URL, "https://query.ai")
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_uuid4():
    """Messagepack can dump/load UUID4 values."""
    data = uuid4()
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_uuid5():
    """Messagepack can dump/load UUID5 values."""
    data = uuid5(NAMESPACE_URL, "https://query.ai")
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_tuples():
    """Messagepack can dump/load tuples of values."""
    data = (42, "fourty-two", 43, 0o1)
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_dict():
    """Messagepack can dump/load dict values."""
    data = {"test": {"a": True, "b": None}}
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_ordered_dict():
    """Messagepack can dump/load OrderedDict instances."""
    data = OrderedDict()
    data["z"] = 9
    data["a"] = 4
    data[0] = 109
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_set():
    """Messagepack can dump/load set values."""
    data = {"test", "a", "b", None}
    out_value = loads(dumps(data))
    assert data == out_value
    assert isinstance(out_value, set)


@pytest.mark.unit
def test_dump_load_frozenset():
    """Messagepack can dump/load frozenset values."""
    data = frozenset(("test", "a", "b", None))
    out_value = loads(dumps(data))
    assert data == out_value
    assert isinstance(out_value, frozenset)


@pytest.mark.unit
def test_dump_load_dataclass():
    """Messagepack can dump/load arbitrary dataclass values."""
    data = SimpleDataclass(a=1, b="2")
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_dump_load_dataclass_slots():
    """Messagepack can dump/load dataclass values where slots=True."""
    if SlotsDataclass is not None:
        # Dataclasses only support the `slots` keyword argument on newer releases of Python
        data = SlotsDataclass(a=1, b="2")
        out_value = loads(dumps(data))
        assert data == out_value


@pytest.mark.unit
def test_msgpack_complex_array():
    """Can serialize an array of multiple types."""
    data = ["foo", "bar", datetime.now(), ("a", "b", "c"), 9, {"a": 1, "b": 3}, 1.2]
    out_value = loads(dumps(data))
    assert data == out_value


@pytest.mark.unit
def test_messpack_list_tuple():
    """Can differentiate between tuples and lists."""
    array_a = ("a", "b", "c")
    array_b = ["a", "b", "c"]

    out_a = loads(dumps(array_a))
    assert isinstance(out_a, tuple)

    out_b = loads(dumps(array_b))
    assert isinstance(out_b, list)

    assert out_a != out_b


@pytest.mark.unit
def test_messpack_set_frozenset():
    """Can differentiate between sets and frozensets."""
    set_a = {"a", "b", "c"}
    set_b = frozenset(("a", "b", "c"))

    out_a = loads(dumps(set_a))
    assert isinstance(out_a, set)
    assert not isinstance(out_a, frozenset)

    out_b = loads(dumps(set_b))
    assert isinstance(out_b, frozenset)
    assert not isinstance(out_b, set)


@pytest.mark.unit
def test_msgpack_v2_message_log_event(message_log_event_v2):
    """Can serialize/deserialize v2 MessageLog event dataclasses."""
    message_log_event_v2.event_payload.external_url = "http://127.0.0.1"
    message_log_event_v2.event_payload.metadata = {"is_neato": False}
    out_value = loads(dumps(message_log_event_v2))
    assert message_log_event_v2 == out_value
    assert isinstance(out_value, EventV2)
    assert isinstance(out_value.event_payload, MessageLog)


@pytest.mark.unit
def test_msgpack_v2_metric_log_event(metric_log_event_v2):
    """Can serialize/deserialize v2 MetricLog event dataclasses."""
    metric_log_event_v2.event_payload.external_url = "http://127.0.0.1"
    metric_log_event_v2.event_payload.metadata = {"is_neato": False}
    out_value = loads(dumps(metric_log_event_v2))
    assert metric_log_event_v2 == out_value
    assert isinstance(out_value, EventV2)
    assert isinstance(out_value.event_payload, MetricLog)


@pytest.mark.unit
def test_msgpack_v2_test_outcomes_event():
    """Can serialize/deserialize v2 TestOutcomes event dataclasses."""
    data = TestOutcomes(
        event_timestamp=None,
        metadata={"is_neato": True},
        external_url="http://127.1.1.1",
        payload_keys=[],
        component=TestGenComponentData(batch_pipeline=None, stream=None, dataset=None, server=None),
        test_outcomes=[
            TestOutcomeItem(
                name="Name-1",
                status=TestStatus.PASSED,
                description="Lots of details; so MANY details really!",
                metadata={},
                start_time=None,
                end_time=None,
                metric_value=Decimal("96.5"),
                metric_name="metric name",
                metric_description="metric description",
                metric_min_threshold=("101.1"),
                metric_max_threshold=Decimal("98.9"),
                integrations=None,
                dimensions=["x", "y"],
                result="test result",
                type="a type",
                key="some key",
            ),
        ],
    )
    out_value = loads(dumps(data))
    assert data == out_value
    assert isinstance(out_value, TestOutcomes)


@pytest.mark.unit
def test_msgpack_v2_batch_pipeline_status_event():
    """Can serialize/deserialize v2 BatchPipelineStatus event dataclasses."""
    data = BatchPipelineStatus(
        event_timestamp=None,
        metadata={"is_neato": None},
        external_url="http://0.0.0.0",
        payload_keys=["p1", "p2"],
        batch_pipeline_component=BatchPipelineData(
            batch_key="batch-key-1",
            run_key="run-key-1",
            run_name=None,
            task_key=None,
            task_name=None,
            details=None,
        ),
        status=RunStatus.PENDING,
    )
    out_value = loads(dumps(data))
    assert data == out_value
    assert isinstance(out_value, BatchPipelineStatus)


@pytest.mark.unit
def test_unknown_class_dump():
    """Messagepack raises a TypeError on unsupported types."""

    class UnknownKlass:
        value = 6

    with pytest.raises(TypeError):
        dumps(UnknownKlass)

    with pytest.raises(TypeError):
        dumps(UnknownKlass())


@pytest.mark.unit
def test_flo_dump_load():
    """Messagepack can dump/load datetime.datetime values."""
    expected = {
        "r": {"a": True, "b": None},
        42: (None, False, False, 1, 42.1415927),
        "m": {"w": ("s", 66, 0x42)},
    }
    flo = BytesIO()
    dump(expected, flo)
    assert flo.getvalue()
    flo.seek(0)

    actual = load(flo)
    assert expected == actual
