from enum import IntFlag
from functools import reduce

# These two constants should be used whenever possible instead of the bare strings
OWNER_ROLE_NAME = "Owner"
MEMBER_ROLE_NAME = "Member"
SYSTEM_ROLE_NAMES = [OWNER_ROLE_NAME, MEMBER_ROLE_NAME]


class Permission(IntFlag):
    READ = 1
    UPDATE = 2
    DEACTIVATE = 4
    ASSIGN = 8
    RUN = 16
    CREATE_CHILDREN = 32

    @staticmethod
    def all() -> int:
        return (
            Permission.READ
            | Permission.UPDATE
            | Permission.DEACTIVATE
            | Permission.ASSIGN
            | Permission.RUN
            | Permission.CREATE_CHILDREN
        )

    @staticmethod
    def none() -> int:
        return 0

    @staticmethod
    def member() -> int:
        return Permission.READ

    @staticmethod
    def owner() -> int:
        return Permission.all()

    @staticmethod
    def from_string_list(string_list: list[str]) -> int:
        perm_list = [Permission(Permission._member_map_[i.upper()].value) for i in string_list]
        return reduce(reduce_permissions, perm_list, 0)

    @staticmethod
    def to_string_list(flags: int) -> list[str]:
        return [k.upper() for k, v in Permission._member_map_.items() if flags & v.value == v.value]

    @staticmethod
    def to_int(permissions: list["Permission"]) -> int:
        return reduce(reduce_permissions, list(permissions), 0)


def reduce_permissions(base: int, perm: Permission) -> int:
    return base | perm.value
