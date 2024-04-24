import pytest
from peewee import CharField

from common.entities import BaseModel
from common.entities.component_meta import ComplexComponentMeta, SimpleComponentMeta


@pytest.mark.unit
def test_simple_component_meta_validation():
    with pytest.raises(ValueError, match="must define"):
        SimpleComponentMeta("SimpleTest", (), {})

    with pytest.raises(ValueError, match="ComplexComponentMeta"):
        SimpleComponentMeta("SimpleTest", (), {"component_type": "simple", "some_field": CharField()})


@pytest.mark.unit
def test_complex_component_meta_validation():
    with pytest.raises(ValueError, match="must define"):
        ComplexComponentMeta("SimpleTest", (BaseModel,), {})

    with pytest.raises(ValueError, match="SimpleComponentMeta"):
        ComplexComponentMeta("SimpleTest", (BaseModel,), {"component_type": "complex"})

    with pytest.raises(ValueError, match="inherit from BaseModel"):
        ComplexComponentMeta("SimpleTest", (), {"component_type": "complex", "some_field": CharField()})
