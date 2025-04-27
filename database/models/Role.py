""" Role Model """

from typing import Optional, List, Self

import discore
from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class Role(Model):
    """Role Model"""

    __casts__ = {'enabled': 'bool'}

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild

    @classmethod
    def find_or_create(cls, guild, role_id: int, guild_kwargs: Optional[dict] = None, **kwargs):
        role = cls.find(role_id)
        if role is None:
            from database.models.Guild import Guild
            if isinstance(guild, int):
                guild = Guild.find_or_create(guild, **(guild_kwargs or {}))
            role = cls.create(
                {'id': role_id, 'guild_id': guild.id, 'enabled': guild.default_role_state, **kwargs}).fresh()
        return role

    @classmethod
    def finds_or_creates(cls, guild, roles_id: list[int], guild_kwargs: Optional[dict] = None, **kwargs) -> List[Self]:
        """
        Check if all roles are enabled
        :param guild: The guild to check
        :param roles_id: The roles to check
        :param guild_kwargs: The guild kwargs
        :param kwargs: The kwargs
        :return: True if all roles are enabled
        """
        # noinspection PyTypeChecker
        db_roles: List[Role] = cls.find(roles_id)
        # noinspection PyUnresolvedReferences
        missing_roles = [role for role in roles_id if role not in [db_role.id for db_role in db_roles]]
        if missing_roles:
            from database.models.Guild import Guild
            if isinstance(guild, int):
                guild = Guild.find_or_create(guild, **(guild_kwargs or {}))
            # noinspection PyUnresolvedReferences
            cls.builder.new().bulk_create([
                {'id': role, 'guild_id': guild.id, 'enabled': guild.default_role_state, **kwargs}
                for role in missing_roles
            ])
            db_roles = cls.where_in('id', roles_id).where('guild_id', guild.id).get()
        # noinspection PyUnresolvedReferences
        return db_roles

    @classmethod
    def update_guild_roles(cls, guild: discore.Guild, ignored_roles: list[int], default_state: bool = True) -> None:
        """
        Update the roles of a guild in the database
        :param guild: The guild to update
        :param ignored_roles: The roles to ignore
        :param default_state: The default state for the created roles
        """

        all_roles = [role.id for role in guild.roles if role.id not in ignored_roles]
        all_db_roles = cls.where('guild_id', guild.id).where_not_in('id', ignored_roles).get()
        missing_from_db = [i for i in all_roles if i not in [c.id for c in all_db_roles]]
        missing_from_discord = [i.id for i in all_db_roles if i.id not in all_roles]
        if missing_from_db:
            # noinspection PyUnresolvedReferences
            cls.builder.new().bulk_create([
                {'id': i, 'guild_id': guild.id, 'enabled': default_state} for i in missing_from_db
            ])
        if missing_from_discord:
            cls.where('guild_id', guild.id).where_in('id', missing_from_discord).delete()

    def __bool__(self):
        if self.is_loaded():
            return self.enabled
        else:
            return bool(super())
