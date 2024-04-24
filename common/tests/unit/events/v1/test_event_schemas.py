import json

import pytest

from common.events.v1 import EventSchema


@pytest.mark.unit
def test_decode_bytes_with_dict(event_data):
    EventSchema().load(event_data)


@pytest.mark.unit
def test_decode_bytes_with_bytes(event_data):
    EventSchema().load(json.dumps(event_data).encode("utf-8"))
