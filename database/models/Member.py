""" Member Model """
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Self

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
            guild: Optional[Guild] = None,
            guild_kwargs: Optional[dict] = None,
            **kwargs
    ) -> Self:
        member = cls.where('user_id', d_member.id).where('guild_id', guild.id).first()
        if member:
            return member

        if guild is None:
            from database.models.Guild import Guild
            guild = Guild.find_or_create(d_member.guild.id, **(guild_kwargs or {}))
        return cls.create({
            'user_id': d_member.id,
            'guild_id': guild.id,
            'on_deny_list': True if d_member.bot else False,
            'bot': d_member.bot,
            **kwargs
        }).fresh()

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
