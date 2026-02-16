""" TextChannel Model """
from __future__ import annotations
from typing import TYPE_CHECKING, Self

import discore

from database.models.AFilterModel import *

if TYPE_CHECKING:
    from database.models.Guild import Guild


class TextChannel(AFilterModel):
    """TextChannel Model"""

    __table__ = "text_channels"

    @classmethod
    def find_or_create(
            cls,
            d_channel: discore.TextChannel,
            guild: Guild | None = None,
            guild_kwargs: dict | None = None,
            **kwargs
    ) -> Self:
        return super().find_or_create(d_channel, guild, guild_kwargs, **kwargs)

    @classmethod
    def find_get_enabled(cls, d_channel: discore.TextChannel, guild: Guild | None = None) -> bool:
        return super().find_get_enabled(d_channel, guild)
