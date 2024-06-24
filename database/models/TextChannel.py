""" TextChannel Model """
from typing import Optional

from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class TextChannel(Model):
    """TextChannel Model"""

    __casts__ = {'enabled': 'bool'}

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild

    @classmethod
    def find_or_create(cls, guild_id, channel_id: int, guild_kwargs: Optional[dict] = None, **kwargs):
        channel = cls.find(channel_id)
        if channel is None:
            from database.models.Guild import Guild
            if isinstance(guild_id, Guild):
                guild = guild_id
            else:
                guild = Guild.find_or_create(guild_id, **(guild_kwargs or {}))
            channel = cls.create({'id': channel_id, 'guild_id': guild.id, **kwargs}).fresh()
        return channel
