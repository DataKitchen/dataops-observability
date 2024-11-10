from typing import Any, Optional, Union

from peewee import Field, ForeignKeyField, ModelBase, ModelSelect, ModelUpdate

from .base_entity import BaseModel
from .component import Component

BASE_COMPONENT_CLASS: type[Component] = Component
"""This is the base Component class."""


class SimpleComponentMeta(ModelBase):
    """
    Metaclass to be used to build Component-based entity classes that do not have additional fields.

    The new component type data will be be stored into the same database table as the base Component entitity. All
    entities using this metaclass should have a `component_type` string field indicating how the new component
    is identified. This value gets stored at the `type` field of the Component entity.
    """

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]) -> type[BaseModel]:
        try:
            component_type: str = str(attrs["component_type"])
        except KeyError as e:
            raise ValueError(f"Component class '{name}' must define the {e} attribute.") from e

        if any(isinstance(v, Field) for v in attrs.values()):
            raise ValueError(
                f"Found additional fields within the '{name}' class definition. "
                "Please use the ComplexComponentMeta meta class instead."
            )

        # When no additional fields are required, we use the same database table as the Component entity, so we make
        # sure it inherits from it.
        if BASE_COMPONENT_CLASS not in bases:
            bases = (BASE_COMPONENT_CLASS, *bases)

        # We also set the table name be the same as the one used by the Component class
        attrs["Meta"] = type("Meta", (), {"table_name": BASE_COMPONENT_CLASS._meta.table_name})

        # Replacing the original Component `type` field with the same field but whose value default to this
        # component's `component_type` value. This spare us of creating custom implementations for the
        # save and create methods that auto-fills the correct value.
        new_component_type_field = BASE_COMPONENT_CLASS._meta.fields["type"].clone()
        new_component_type_field.default = component_type
        attrs["type"] = new_component_type_field

        entity_class: type[BaseModel] = super().__new__(cls, name, bases, attrs)

        def select(cls: type[BaseModel], *fields: object) -> ModelSelect:
            # The join is useful to allow using the Component entity fields in WHERE clauses, regardless of
            # the component class, increasing the compatibility with the components with additional fields
            query = (
                super(cls, cls)
                .select(*fields)
                .join(BASE_COMPONENT_CLASS, on=BASE_COMPONENT_CLASS.id == cls.id)
                .switch(cls)
                .where(cls.type == cls.component_type)
            )
            return query

        def update(cls: type[BaseModel], **fields: object) -> ModelUpdate:
            query = super(cls, cls).update(**fields).where(cls.type == cls.component_type)
            return query

        def delete(cls: type[BaseModel]) -> ModelUpdate:
            query = super(cls, cls).delete().where(cls.type == cls.component_type)
            return query

        entity_class.select = classmethod(select)
        entity_class.update = classmethod(update)
        entity_class.delete = classmethod(delete)

        # No additional DB tables are required for components with no additional fields, so we are silencing
        # the methods that handles creating and dropping the DB tables.
        entity_class.create_table = classmethod(lambda *args, **kwargs: None)
        entity_class.drop_table = classmethod(lambda *args, **kwargs: None)

        # The components with additional fields have a FK to the Component entity, so we also add a property
        # here that behaves the same to make sure the different component type flavors have a compatible API
        entity_class.component = property(lambda self: self)

        # Alias to the `component` property. Provides handy access to the Component entity and fields
        entity_class.c = property(lambda self: self.component)

        # Injecting a convenience method into the Component class that returns the component as its specific type.
        setattr(
            BASE_COMPONENT_CLASS, f"_get_{component_type.lower()}_instance", lambda self: entity_class(**self.__data__)
        )

        return entity_class


class ComplexComponentMeta(ModelBase):
    """
    Metaclass to be used to build Component-based entity classes that have additional fields.

    New types with additional fields will require an specific database table to be created. This new table has a FK
    to the Component table that also serves as its PK. Common data is stored at the Component entity table. All
    entities using this metaclass should have a `component_type` string field indicating how the new component
    is identified. This value gets stored at the `type` field from the Component entity.
    """

    def __new__(cls, name: str, bases: tuple[type, ...], attrs: dict[str, object]) -> type[BaseModel]:
        try:
            component_type: str = str(attrs["component_type"])
        except KeyError as e:
            raise ValueError(f"Component class '{name}' must define the '{e}' attribute.") from e

        if not any(isinstance(v, Field) for v in attrs.values()):
            raise ValueError(
                f"No additional fields found in '{name}' class definition. "
                "Please use the SimpleComponentMeta meta class instead."
            )

        if not any(issubclass(b, BaseModel) for b in bases):
            raise ValueError(f"{name} entity class has to inherit from BaseModel or any of its subclasses.")

        base_fields = BASE_COMPONENT_CLASS._meta.fields.keys()

        attrs["component"] = ForeignKeyField(
            BASE_COMPONENT_CLASS,
            primary_key=True,
            backref=component_type,
            # We want the components with additional fields to have a "id" attribute for its ID, but its
            # primary key is named "component" and is an FK field, so we are overriding the object_id_name
            # of the FK to be the Component PK name ("id").
            object_id_name=BASE_COMPONENT_CLASS._meta.primary_key.name,
            on_delete="CASCADE",
        )

        entity_class: type[BaseModel] = super().__new__(cls, name, bases, attrs)

        def select(cls: type[BaseModel], *fields: object) -> ModelSelect:
            query = super(cls, cls).select(*fields, BASE_COMPONENT_CLASS).join(BASE_COMPONENT_CLASS)
            return query

        def create(cls: type[BaseModel], **data: object) -> BaseModel:
            base_args = {k: v for k, v in data.items() if k in base_fields}
            base_component = BASE_COMPONENT_CLASS.create(type=cls.component_type, **base_args)

            component_args = {k: v for k, v in data.items() if k not in base_fields}
            component = cls(component=base_component, **component_args)
            component.save(force_insert=True)
            return component

        def save(self: BaseModel, force_insert: bool = False, only: Optional[object] = None) -> Union[bool, int]:
            ret = 0
            if not force_insert and self.component:
                ret += self.component.save(only=only) or 0
            ret += super(entity_class, self).save(force_insert=force_insert, only=only) or 0
            return ret or False

        entity_class.select = classmethod(select)
        entity_class.create = classmethod(create)
        entity_class.save = save

        # Alias to the `component` property. Provides handy access to the Component entity and fields
        entity_class.c = property(lambda self: self.component)

        # Injecting a convenience method into the Component class that returns the component as its specific type.
        def get_type_instance_func(self: Any) -> BaseModel:
            """Retrieves the entity that holds the additional fields."""
            # For this to work, the backref of the FK to Component must be named using `component_type`
            instance: BaseModel = getattr(self, component_type).get()
            return instance

        setattr(BASE_COMPONENT_CLASS, f"_get_{component_type.lower()}_instance", get_type_instance_func)

        return entity_class
