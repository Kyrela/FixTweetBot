""" Member Model """
from __future__ import annotations
from typing import TYPE_CHECKING, Self

import discore

from database.models.AFilterModel import *

if TYPE_CHECKING:
    from database.models.Guild import Guild


class Member(AFilterModel):
    """Member Model"""

    __table__ = "members"

    @classmethod
    def find_or_create(
            cls,
            d_member: discore.Member,
            guild: Guild | None = None,
            guild_kwargs: dict | None = None,
            **kwargs
    ) -> Self:
        if guild is None:
            from database.models.Guild import Guild
            guild = Guild.find_or_create(d_member.guild, **(guild_kwargs or {}))

        member = cls.where('user_id', d_member.id).where('guild_id', guild.id).first()
        if member:
            return member

        return cls.create({
            'user_id': d_member.id,
            'guild_id': guild.id,
            'on_deny_list': True if d_member.bot else False,
            'bot': d_member.bot,
            **kwargs
        }).fresh()

    @classmethod
    def find_get_enabled(cls, d_member: discore.Member, guild: Guild | None = None) -> bool:
        if not guild:
            return not d_member.bot
        element = cls.where('user_id', d_member.id).where('guild_id', guild.id).first()
        if element:
            return element.enabled(guild)
        if guild[f'{cls.__table__}_use_allow_list']:
            return False
        return not d_member.bot

    @classmethod
    def reset_lists(cls, guild: Guild) -> None:
        """
        Reset the deny and allow lists for all members in a guild.
        :param guild: The guild to reset the lists for.
        """
        cls.where('guild_id', guild.id).update({
            'on_allow_list': False
        })
        cls.where('guild_id', guild.id).where('bot', False).update({
            'on_deny_list': False
        })
        cls.where('guild_id', guild.id).where('bot', True).update({
            'on_deny_list': True
        })
