__all__ = ["Project"]

from peewee import CharField, ForeignKeyField, IntegerField

from .base_entity import ActivableEntityMixin, AuditEntityMixin, BaseEntity
from .organization import Organization
from conf import settings
from common.peewee_extensions.fields import JSONSchemaField
from common.schemas.action_schemas import ActionSchema


class Project(BaseEntity, ActivableEntityMixin, AuditEntityMixin):
    """Third (and currently final) tier of the organizational hierarchy"""

    name = CharField(null=False)
    description = CharField(null=True)
    organization = ForeignKeyField(Organization, backref="projects", on_delete="CASCADE", null=False, index=True)

    # Settings
    agent_check_interval = IntegerField(null=False, default=settings.AGENT_STATUS_CHECK_DEFAULT_INTERVAL_SECONDS)
    alert_actions = JSONSchemaField(ActionSchema(many=True), null=False, default=[])

    class Meta:
        indexes = ((("organization", "name"), True),)
