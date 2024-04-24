import pytest
from peewee import CharField, SqliteDatabase

from common.entities import (
    ALL_MODELS,
    DB,
    Action,
    AuditUpdateTimeEntityMixin,
    BaseEntity,
    Company,
    Dataset,
    Instance,
    InstanceSet,
    Journey,
    Organization,
    Pipeline,
    Project,
    Run,
    RunStatus,
    TestOutcome,
)


@pytest.fixture
def test_db():
    DB.initialize(SqliteDatabase(":memory:", pragmas={"foreign_keys": 1}))
    yield DB
    DB.obj = None


class AuditUpdateTimeEntityClass(BaseEntity, AuditUpdateTimeEntityMixin):
    name = CharField(unique=False, null=True)


@pytest.fixture(autouse=True)
def test_base(test_db):
    test_db.create_tables([*ALL_MODELS, AuditUpdateTimeEntityClass])
    yield test_db
    test_db.drop_tables([*ALL_MODELS, AuditUpdateTimeEntityClass])
    test_db.close()


@pytest.fixture
def audit_update_obj():
    a = AuditUpdateTimeEntityClass.create(name="A")
    yield a


@pytest.fixture
def company():
    c = Company.create(name="Fake Company")
    yield c


@pytest.fixture
def organization(company):
    org = Organization.create(name="Fake Organization", company=company)
    yield org


@pytest.fixture
def project(organization):
    prog = Project.create(name="Fake Project", organization=organization)
    yield prog


@pytest.fixture
def instance(journey):
    return Instance.create(journey=journey)


@pytest.fixture
def instance_set(patched_instance_set, instance):
    return InstanceSet.get_or_create([instance.id])


@pytest.fixture
def pipeline(project):
    pipe = Pipeline.create(key="Fake Pipeline", project=project)
    yield pipe


@pytest.fixture
def pipeline_run(pipeline, instance_set):
    run = Run.create(key="mykey", pipeline=pipeline, instance_set=instance_set, status=RunStatus.RUNNING.name)
    yield run


@pytest.fixture
def dataset(project):
    yield Dataset.create(project=project, key="DS1", name="Dataset One")


@pytest.fixture
def action(company):
    yield Action.create(name="Fake Action", action_impl="SEND_EMAIL", company=company)


@pytest.fixture()
def journey(project):
    return Journey.create(name="J1", project=project)


@pytest.fixture
def test_outcome(pipeline):
    return TestOutcome.create(component=pipeline, name="test-outcome-entity-test-1", status="test-status")
