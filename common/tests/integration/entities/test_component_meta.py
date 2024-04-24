from unittest.mock import patch
from uuid import UUID

import pytest
from peewee import CharField

from common.entities import BaseModel, Component
from common.entities.component_meta import ComplexComponentMeta, SimpleComponentMeta


class SimpleComponent(BaseModel, metaclass=SimpleComponentMeta):
    component_type = "simple_type"


class ComplexComponent(BaseModel, metaclass=ComplexComponentMeta):
    component_type = "complex_type"
    additional_field = CharField(max_length=12)


@pytest.fixture()
def component_db(test_db):
    test_db.create_tables([SimpleComponent, ComplexComponent])
    yield test_db
    test_db.drop_tables([SimpleComponent, ComplexComponent])


@pytest.fixture
def simple_component_data(project):
    return {
        "project": project.id,
        "key": "simple_key",
        "name": "Simple Component",
        "description": None,
    }


@pytest.fixture
def complex_component_data(project):
    return {
        "project": project.id,
        "key": "complex_key",
        "name": "Complex Component",
        "additional_field": "additional data",
        "description": None,
    }


@pytest.fixture
def simple_component(component_db, simple_component_data):
    return SimpleComponent.create(**simple_component_data)


@pytest.fixture
def complex_component(component_db, complex_component_data):
    return ComplexComponent.create(**complex_component_data)


@pytest.fixture
def assorted_components(project):
    c_instances = []
    c_classes = []
    for i in range(10):
        if i % 3 == 0:
            attrs = {"component_type": f"complex_{i}", "some_field": CharField()}
            meta_class = ComplexComponentMeta
        else:
            attrs = {"component_type": f"simple_{i}"}
            meta_class = SimpleComponentMeta

        c_class = meta_class(f"ComponentClass{i}", (BaseModel,), attrs)
        c_class.create_table()
        c_classes.append(c_class)

        for ii in range(2):
            instance_idx = i * 2 + ii
            c_instances.append(
                c_class.create(
                    project=project.id,
                    key=f"instance_{instance_idx}",
                    name=f"This is the component #{instance_idx}",
                    some_field="some data",
                )
            )
    yield c_classes, c_instances
    for c_class in c_classes:
        c_class.drop_table()


@pytest.mark.integration
def test_simple_save_force_insert(simple_component_data):
    instance = SimpleComponent(**simple_component_data)
    instance.save(force_insert=True)
    assert instance.type == "simple_type"
    assert isinstance(instance.id, UUID)
    assert Component.select().count() == 1
    assert SimpleComponent.select().count() == 1, str(SimpleComponent.select())


@pytest.mark.integration
def test_complex_save_force_insert(component_db, complex_component_data):
    component = Component(type="complex_type", **complex_component_data)
    component.save(force_insert=True)
    instance = ComplexComponent(component=component, **complex_component_data)
    instance.save(force_insert=True)
    assert Component.select().count() == 1
    assert ComplexComponent.select().count() == 1, str(ComplexComponent.select())


@pytest.mark.integration
@pytest.mark.parametrize(
    "component_class,data_fixture",
    (
        (SimpleComponent, "simple_component_data"),
        (ComplexComponent, "complex_component_data"),
    ),
    ids=("simple component", "complex component"),
)
def test_create(component_class, data_fixture, component_db, request):
    instance = component_class.create(**request.getfixturevalue(data_fixture))
    assert instance.c.type == component_class.component_type
    assert isinstance(instance.id, UUID)
    assert instance.id == instance.c.id
    assert Component.select().count() == 1
    assert component_class.select().count() == 1, str(component_class.select())


@pytest.mark.integration
@pytest.mark.parametrize(
    "component_class,expected_calls", ((SimpleComponent, 0), (ComplexComponent, 2)), ids=("simple", "complex")
)
def test_table_create_and_drop(component_class, expected_calls, component_db):
    with patch.object(component_db.obj, "execute_sql") as sql_mock:
        component_db.create_tables([component_class])
        component_db.drop_tables([component_class])
    assert sql_mock.call_count == expected_calls


@pytest.mark.integration
@pytest.mark.parametrize("component_fixture", ("simple_component", "complex_component"))
def test_get_base_component(component_fixture, request):
    child_component = request.getfixturevalue(component_fixture)
    base_component = child_component.component
    base_component_2 = child_component.c

    assert base_component is base_component_2
    assert issubclass(type(base_component), Component)
    assert base_component.id == child_component.id


@pytest.mark.integration
@pytest.mark.parametrize("component_fixture", ("simple_component", "complex_component"))
def test_get_specific_component(component_fixture, request):
    expected_component = request.getfixturevalue(component_fixture)
    base_component = Component.select().where(Component.key == expected_component.c.key).get()

    component = base_component.type_instance

    assert type(component) == type(expected_component)
    assert component == expected_component
    assert component.id == base_component.id


@pytest.mark.integration
def test_select(assorted_components):
    (complex_class, simple_class, *_), instances = assorted_components
    assert Component.select().count() == 20
    assert complex_class.select().count() == 2
    assert simple_class.select().count() == 2
    assert Component.select(Component.type).distinct().count() == 10
    assert Component.select(Component.key).distinct().count() == 20
    assert type(complex_class.select().get()) == complex_class
    assert type(simple_class.select().get()) == simple_class
    assert type(Component.select().get()) == Component


@pytest.mark.integration
def test_select_with_filter_simple(simple_component):
    assert Component.select().where(Component.key == "simple_key").count() == 1
    assert SimpleComponent.select().where(SimpleComponent.key == "simple_key").count() == 1


@pytest.mark.integration
def test_select_with_filter_complex(complex_component):
    assert Component.select().where(Component.key == "complex_key").count() == 1
    assert ComplexComponent.select().where(Component.key == "complex_key").count() == 1


@pytest.mark.integration
@pytest.mark.parametrize(
    "component_class,key",
    ((SimpleComponent, "simple_key"), (ComplexComponent, "complex_key")),
    ids=("simple", "complex"),
)
def test_select_filter_by_component_field(component_class, key, simple_component, complex_component):
    assert Component.select().count() == 2
    assert Component.select().where(Component.key == key).count() == 1
    assert component_class.select().where(Component.key == key).count() == 1


@pytest.mark.integration
@pytest.mark.parametrize("component_fixture", ("simple_component", "complex_component"))
def test_save_base_field_changed(component_fixture, request):
    component = request.getfixturevalue(component_fixture)
    component.c.key = "some_new_key"

    assert component.save() == 1
    assert Component.select().where(Component.key == "some_new_key").count() == 1


@pytest.mark.integration
def test_save_complex_row_count(complex_component):
    # not dirty
    assert complex_component.save() is False

    # base dirty
    complex_component.c.key = "some_new_key"
    assert complex_component.save() == 1

    # component dirty
    complex_component.additional_field = "new value"
    assert complex_component.save() == 1

    # both dirty
    complex_component.c.key = "some_new_key"
    complex_component.additional_field = "new value"
    assert complex_component.save() == 2


@pytest.mark.integration
def test_save_complex(complex_component):
    complex_component.additional_field = "other value"
    complex_component.save()

    assert ComplexComponent.select().where(ComplexComponent.additional_field == "other value").count() == 1


@pytest.mark.integration
def test_update(assorted_components):
    (complex_class, simple_class, *_), instances = assorted_components

    assert complex_class.update(some_field="some other value").execute() == 2
    assert simple_class.update(name="some other value").execute() == 2
    assert Component.update(name="yet another value").execute() == 20


@pytest.mark.integration
def test_delete(assorted_components):
    (complex_class, simple_class, *_), instances = assorted_components

    assert complex_class.delete().execute() == 2
    assert simple_class.delete().execute() == 2
    assert Component.delete().execute() == 18
