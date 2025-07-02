""" TextChannel Model """
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Self

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
            guild: Optional[Guild] = None,
            guild_kwargs: Optional[dict] = None,
            **kwargs
    ) -> Self:
        return super().find_or_create(d_channel, guild, guild_kwargs, **kwargs)
