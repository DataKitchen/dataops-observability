from datetime import datetime

import pytest

from common.entities import Instance


@pytest.mark.integration
def test_instance_active_property(instance):
    instance.end_time = None
    assert instance.active is True

    instance.end_time = datetime.utcnow()
    assert instance.active is False


@pytest.mark.integration
def test_instance_active_query(instance):
    instance.end_time = None
    instance.save()
    assert 1 == Instance.select().where(Instance.active == True).count()

    instance.end_time = datetime.utcnow()
    instance.save()
    assert 1 == Instance.select().where(Instance.active == False).count()
