""" Member Model """
from __future__ import annotations

from typing import Optional, TYPE_CHECKING

import discore
from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to

if TYPE_CHECKING:
    from database.models.Guild import Guild


class Member(Model):
    """Member Model"""

    __casts__ = {'enabled': 'bool'}

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild

    @classmethod
    def find_or_create(cls, d_member: discore.Member, guild: Optional[Guild] = None, guild_kwargs: Optional[dict] = None, **kwargs):
        member = cls.where('user_id', d_member.id).where('guild_id', guild.id).first()
        if member:
            return member

        if guild is None:
            from database.models.Guild import Guild
            guild = Guild.find_or_create(d_member.guild.id, **(guild_kwargs or {}))
        return cls.create({
            'user_id': d_member.id,
            'guild_id': d_member.guild.id,
            'enabled': guild.default_member_state if not d_member.bot else False,
            'bot': d_member.bot,
            **kwargs
        }).fresh()

    @classmethod
    def update_guild_members(cls, guild: discore.Guild, ignored_members: list[int], default_state: bool = True) -> None:
        """
        Update the members of a guild
        :param guild: The guild to update the members for
        :param ignored_members: A list of member IDs to ignore
        :param default_state: The default state for the created members
        :return: None
        """

        all_members = [member for member in guild.members if member.id not in ignored_members]
        all_db_members = cls.where('guild_id', guild.id).where_not_in('user_id', ignored_members).get()
        missing_from_db = [
            member for member in all_members if member.id not in [db_member.user_id for db_member in all_db_members]]
        missing_from_discord = [member.user_id for member in all_db_members if member.user_id not in [m.id for m in all_members]]
        if missing_from_db:
            # noinspection PyUnresolvedReferences
            cls.builder.new().bulk_create([
                {
                    'user_id': member.id,
                    'guild_id': guild.id,
                    'enabled': default_state if not member.bot else False,
                    'bot': member.bot
                } for member in missing_from_db
            ])
        if missing_from_discord:
            cls.where('guild_id', guild.id).where_in('user_id', missing_from_discord).delete()

