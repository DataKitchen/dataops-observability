import logging
from base64 import b64decode, b64encode
from collections import OrderedDict
from functools import cache
from graphlib import CycleError, TopologicalSorter
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

# TODO: When we move to Python 3.11+ we can switch to importing tomlib and we can remove the tomli requirement from
# pyproject.toml -- tomlib *is* tomli and it is being pulled into the standard library as part of PEP-680
import tomli
from jinja2 import Environment, FileSystemLoader, select_autoescape
from peewee import BlobField, BooleanField, DoesNotExist, IntegerField, IntegrityError, Model, ModelSelect, UUIDField

from common.entities import DB
from common.model import walk

TEMPLATE_DIR = Path(__file__).resolve().parent.joinpath("templates")
JINJA_ENV = Environment(loader=FileSystemLoader(TEMPLATE_DIR), autoescape=select_autoescape())
LOG = logging.getLogger(__name__)


def toml_value(field_data: dict[str, Any]) -> str:
    """Convert data to a form valid for toml output."""
    field_instance = field_data["field_instance"]
    value = field_data["value"]

    # Binary fields can be bytes or memoryviews and have to be handled without db conversion
    if isinstance(field_instance, BlobField):
        return f'"{b64encode(value).decode("utf-8")}"'
    if isinstance(field_instance, BooleanField):
        return "true" if value is True else "false"
    if isinstance(field_instance, IntegerField):
        return str(value)

    # Convert the field value to the value the ORM would send to the Database
    db_value = field_instance.db_value(value)

    # Special handling for UUID field types
    if isinstance(field_instance, UUIDField):
        return f'"{str(UUID(db_value))}"'
    return f'"{db_value}"'


JINJA_ENV.filters["toml_value"] = toml_value


class FixtureDependencyError(ValueError):
    pass


@cache
def generate_table_map() -> dict[str, Model]:
    """Remap model schema by table_name."""
    model_map = walk()
    return {x._meta.table_name: x for x in model_map.values()}


def dump_results(results: ModelSelect, *, requires_id: UUID | None = None) -> str:
    """Given Peewee query results, generate a fixture dump."""
    model_class = results.model
    rows = []
    fields = model_class._meta.fields
    for instance in results:
        data = OrderedDict()
        for attr_name in sorted(fields.keys()):
            field_instance = fields[attr_name]
            data[attr_name] = {
                "field_instance": field_instance,
                "value": getattr(instance, attr_name),
            }
        rows.append(data)

    context = {
        "table_name": model_class._meta.table_name,
        "fixture_id": uuid4(),
        "requires_id": requires_id,
        "rows": rows,
    }
    template = JINJA_ENV.get_template("model.toml")
    result = template.render(**context)
    return result


def dependency_sort(fixture_list: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """
    Sort a set of fixtures according to their dependency stack.
    """
    graph = {}
    nodes = {}
    for fixture in fixture_list:
        nodes[fixture["fixture_id"]] = fixture
        if requires := fixture.get("requires_id"):
            graph[fixture["fixture_id"]] = {requires}
        else:
            # No dependency stated.
            graph[fixture["fixture_id"]] = set()
    try:
        # see: https://docs.python.org/3/library/graphlib.html
        ordered_ids = list(TopologicalSorter(graph).static_order())
        sorted_fixtures = [nodes[fixture_id] for fixture_id in ordered_ids]
        return sorted_fixtures
    except CycleError as e:
        raise FixtureDependencyError(str(e)) from e
    except KeyError as k:
        raise FixtureDependencyError(f"Unknown Fixture: {k}") from k


def apply_fixture(fixture_dict: dict[str, Any], overwrite: bool = False) -> None:
    """Given a set of fixture data, insert into the database."""
    table_map = generate_table_map()
    model_class = table_map[fixture_dict["table_name"]]
    fields = model_class._meta.fields

    LOG.info("Applying %s fixture: %s", fixture_dict["table_name"], fixture_dict["fixture_id"])

    # Check for the presence of a primary key and identify any binary fields which need to be base64 decoded
    pk_field = None
    pk_field_name = ""
    binary_fields = []

    for field_name, field_instance in fields.items():
        if field_instance.primary_key is True:
            pk_field = field_instance
            pk_field_name = field_name
        if isinstance(field_instance, BlobField):
            binary_fields.append(field_name)

    # If we have a primary-key to query on, use "get_or_create"
    if pk_field and pk_field_name:
        for row_dict in fixture_dict.get("row", ()):
            # Transform the serialized values into python values according to the model fields
            transformed_dict = {}
            for k, v in row_dict.items():
                if k in binary_fields:
                    try:
                        v = b64decode(v)
                    except Exception:
                        LOG.warning("Unable to decode %s value as base64: %s", k, v)
                transformed_dict[k] = fields[k].python_value(v)
            try:
                instance = model_class.get(**{pk_field_name: transformed_dict[pk_field_name]})
            except DoesNotExist:
                instance = model_class(**transformed_dict)
                instance.save(force_insert=True)
                LOG.debug("Created: %s", instance)
            else:
                if overwrite is True:
                    for attr_name, value in transformed_dict.items():
                        if attr_name == pk_field_name:
                            continue  # Skip - already set and cannot be changed
                        setattr(instance, attr_name, value)
                    instance.save()
                    LOG.debug("Updated: %s", instance)
                else:
                    raise ValueError(f"Not overwriting existing data in: {instance}")
    else:
        # Without a primary key just try a create
        for row_dict in fixture_dict.get("row", ()):
            # Transform the serialized values into python values according to the model fields
            transformed_dict = {k: fields[k].python_value(v) for k, v in row_dict.items()}
            try:
                instance = model_class(**transformed_dict)
                instance.save(force_insert=True)
            except IntegrityError:
                LOG.exception("Unable to create database row using loaded data: %s", transformed_dict)
                raise
            else:
                LOG.debug("Wrote: %s", instance)


def read_file(path: Path) -> dict[str, Any]:
    """Read and parse a toml file."""
    if not path.is_file():
        raise ValueError(f"Path `{path}` is not a file")
    LOG.info("Reading fixture: %s", path)
    with path.open("rb") as f:
        fixture_dict = tomli.load(f)
    return fixture_dict


def read_folder(folder: Path, *, recursive: bool = True) -> list[dict[str, Any]]:
    """Read a folder of fixtures and return sorted according to dependencies."""
    if not folder.is_dir():
        raise ValueError(f"Path `{folder}` is not a folder")
    glob_pattern = "**/*.toml" if recursive is True else "*.toml"
    unsorted_fixtures = [read_file(x) for x in folder.glob(glob_pattern)]
    return dependency_sort(unsorted_fixtures)


def load_file(path: Path, overwrite: bool = True) -> None:
    """Load a fixture file and apply it to the database."""
    with DB.obj.atomic():
        apply_fixture(read_file(path), overwrite=overwrite)


def load_folder(path: Path, overwrite: bool = True, recursive: bool = True) -> None:
    """Load a folder and apply all it's fixtures to the database."""
    with DB.obj.atomic():
        for fixture_dict in read_folder(path, recursive=recursive):
            apply_fixture(fixture_dict, overwrite=overwrite)
