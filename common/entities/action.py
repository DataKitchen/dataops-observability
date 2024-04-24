__all__ = ["Action", "ActionImpl"]

from enum import Enum
from peewee import CharField, ForeignKeyField
from common.peewee_extensions.fields import EnumStrField
from playhouse.mysql_ext import JSONField

from .base_entity import BaseEntity
from .company import Company



class ActionImpl(Enum):
    SEND_EMAIL = "SEND_EMAIL"
    CALL_WEBHOOK = "CALL_WEBHOOK"


class Action(BaseEntity):
    """Represents an action to execute when a rule evaluates to true"""

    name = CharField(null=False)
    company = ForeignKeyField(Company, backref="actions", on_delete="CASCADE", null=False, index=True)
    action_impl = EnumStrField(ActionImpl, null=False)
    action_args = JSONField(default=dict, null=False)

    class Meta:
        indexes = ((("name", "company"), True),)  # action name must be unique in company
        table_name = "action"
