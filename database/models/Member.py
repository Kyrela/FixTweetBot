""" Member Model """

from typing import Optional

import discore
from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class Member(Model):
    """Member Model"""

    __casts__ = {'enabled': 'bool'}

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild

    @classmethod
    def find_or_create(cls, guild, member_id: int, guild_kwargs: Optional[dict] = None, **kwargs):
        member = cls.find(member_id)
        if member is None:
            from database.models.Guild import Guild
            if isinstance(guild, int):
                guild = Guild.find_or_create(guild, **(guild_kwargs or {}))
            member = cls.create(
                {'id': member_id, 'guild_id': guild.id, 'enabled': guild.default_member_state, **kwargs}).fresh()
        return member

    @classmethod
    def update_guild_members(cls, guild: discore.Guild, ignored_members: list[int], default_state: bool = True) -> None:
        """
        Update the members of a guild
        :param guild: The guild to update the members for
        :param ignored_members: A list of member IDs to ignore
        :param default_state: The default state for the created members
        :return: None
        """

        all_members = [member.id for member in guild.members if member.id not in ignored_members and not member.bot]
        all_db_members = cls.where('guild_id', guild.id).where_not_in('id', ignored_members).get()
        missing_from_db = [member for member in all_members if member not in [db_member.id for db_member in all_db_members]]
        missing_from_discord = [member.id for member in all_db_members if member.id not in all_members]
        if missing_from_db:
            # noinspection PyUnresolvedReferences
            cls.builder.new().bulk_create([
                {'id': member, 'guild_id': guild.id, 'enabled': default_state} for member in missing_from_db
            ])
        if missing_from_discord:
            cls.where('guild_id', guild.id).where_in('id', missing_from_discord).delete()

