""" Role Model """
from __future__ import annotations
from typing import List, Self, TYPE_CHECKING

import discore

from database.models.AFilterModel import *

if TYPE_CHECKING:
    from database.models.Guild import Guild


class Role(AFilterModel):
    """Role Model"""

    __table__ = "roles"

    @classmethod
    def find_or_create(
            cls,
            d_role: discore.Role,
            guild: Guild | None = None,
            guild_kwargs: dict | None = None,
            **kwargs
    ) -> Self:
        return super().find_or_create(d_role, guild, guild_kwargs, **kwargs)

    @classmethod
    def find_get_enabled(cls, d_role: discore.Role, guild: Guild | None = None) -> bool:
        return super().find_get_enabled(d_role, guild)

    @classmethod
    def finds_get_enabled(cls, d_roles: list[discore.Role], guild: Guild | None = None) -> List[bool]:
        """
        Get the enabled status of multiple roles. The order and size of the returned list are not guaranteed
        to match the input list.
        :param d_roles: A list of discore.Role instances
        :param guild: The guild to which the roles belong
        :return: A list of boolean values indicating whether roles are enabled
        """
        if not guild:
            return [True]

        roles_id = {role.id for role in d_roles}
        db_roles: List[Role] = cls.where_in('id', list(roles_id)).get()

        results = [role.enabled(guild) for role in db_roles]

        found_roles_id = {role.id for role in db_roles}
        missing_roles_count = len(roles_id) - len(found_roles_id)

        if missing_roles_count > 0:
            default_status = not guild[f'{cls.__table__}_use_allow_list']
            results.extend([default_status] * missing_roles_count)

        return results
