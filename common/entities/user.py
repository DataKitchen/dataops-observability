__all__ = ["User", "Role", "UserRole"]

from peewee import CharField, Check, ForeignKeyField
from playhouse.hybrid import hybrid_property

from common.constants import ADMIN_ROLE

from .base_entity import ActivableEntityMixin, AuditEntityMixin, BaseEntity
from .company import Company


class User(BaseEntity, ActivableEntityMixin, AuditEntityMixin):
    """
    Representation of a user in the system.  Contains only necessary metadata for the app, and defers anything
    else to the storage of the AuthProvider the user is linked to through their `primary_company`.
    """

    name = CharField(null=False)  # Single field for all parts of a user's full name
    email = CharField(index=True, null=False)
    # This needs to be nullable so that we can support our two-part user creation process.
    foreign_user_id = CharField(index=True, null=True)  # Unique ID provided by the AuthProvider
    # Every user belongs to a single Company as their "primary" -- this helps identify how to authenticate them.
    primary_company = ForeignKeyField(Company, backref="users", on_delete="CASCADE", null=False, index=True)
    username = CharField(null=True)
    # Make sure password does not contain ':'
    password = CharField(null=True)
    salt = CharField(null=True)

    @property
    def user_roles(self) -> list[str]:
        roles = Role.select().join(UserRole).join(User).where(User.id == self.id)
        return [x.name for x in roles]

    def has_role(self, name: str) -> bool:
        """Determine if the user is a member of the role."""
        return name in self.user_roles

    @hybrid_property  # type: ignore [misc]
    def admin(self) -> bool:
        return ADMIN_ROLE in self.user_roles

    class Meta:
        # Multi-column indexes
        indexes = (
            # Unique index across primary company + foreign_user_id
            (("primary_company", "foreign_user_id"), True),
            (("primary_company", "email"), True),
            (("username",), True),
        )
        constraints = [
            Check(
                "(not (username like '%%:%%'))",
                "username_special_character",
            )
        ]


class Role(BaseEntity):
    """
    Describes a "Role"; roles are essentially groups. They are used by endpoints to determine whether a user may
    perform actions on the endpoints.
    """

    name = CharField(null=False, unique=True)
    description = CharField(null=True)

    class Meta:
        table_name = "rbac_role"


class UserRole(BaseEntity):
    """A through table for a m2m relationship between users and roles."""

    user = ForeignKeyField(User, on_delete="CASCADE", null=False, index=True)
    role = ForeignKeyField(Role, on_delete="CASCADE", null=False, index=True)

    class Meta:
        table_name = "user_role_through_table"
