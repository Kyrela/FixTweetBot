""" Role Model """
from __future__ import annotations
from typing import Optional, List, Self, TYPE_CHECKING

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
            guild: Optional[Guild] = None,
            guild_kwargs: Optional[dict] = None,
            **kwargs
    ) -> Self:
        return super().find_or_create(d_role, guild, guild_kwargs, **kwargs)

    @classmethod
    def finds_or_creates(cls, d_roles: list[discore.Role], guild: Optional[Guild] = None, guild_kwargs: Optional[dict] = None, **kwargs) -> List[Self]:
        """
        Find or create multiple roles in the database.
        :param d_roles: A list of discore.Role instances to find or create
        :param guild: The guild to which the roles belong
        :param guild_kwargs: Additional keyword arguments for creating the guild if it does not exist
        :param kwargs: Additional keyword arguments for creating the roles if they do not exist
        :return: A list of Role instances
        """

        roles_id = [role.id for role in d_roles]
        db_roles: List[Role] = cls.find(roles_id)
        missing_roles = [role for role in roles_id if role not in [db_role.id for db_role in db_roles]]
        if not missing_roles:
            return db_roles

        if guild is None:
            from database.models.Guild import Guild
            guild = Guild.find_or_create(d_roles[0].guild.id, **(guild_kwargs or {}))
        # noinspection PyUnresolvedReferences
        cls.builder.new().bulk_create([
            {'id': role, 'guild_id': guild.id, **kwargs}
            for role in missing_roles
        ])
        return cls.where_in('id', roles_id).where('guild_id', guild.id).get()
