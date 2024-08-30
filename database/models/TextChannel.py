""" TextChannel Model """
from typing import Optional

import discore
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
    def find_or_create(cls, guild, channel_id: int, guild_kwargs: Optional[dict] = None, **kwargs):
        channel = cls.find(channel_id)
        if channel is None:
            from database.models.Guild import Guild
            if isinstance(guild, int):
                guild = Guild.find_or_create(guild, **(guild_kwargs or {}))
            channel = cls.create(
                {'id': channel_id, 'guild_id': guild.id, 'enabled': guild.default_channel_state, **kwargs}).fresh()
        return channel

    @classmethod
    def update_guild_channels(cls, guild: discore.Guild, ignored_channels: list[int], default_state: bool = True) -> None:
        """
        Update the channels of a guild in the database
        :param guild: The guild to update
        :param ignored_channels: The channels to ignore
        :param default_state: The default state for the created channels
        """

        all_channels = [channel.id for channel in guild.text_channels + [*guild.threads]
                        if channel.id not in ignored_channels]
        all_db_channels = cls.where('guild_id', guild.id).where_not_in('id', ignored_channels).get()
        missing_from_db = [i for i in all_channels if i not in [c.id for c in all_db_channels]]
        missing_from_discord = [i.id for i in all_db_channels if i.id not in all_channels]
        if missing_from_db:
            # noinspection PyUnresolvedReferences
            cls.builder.new().bulk_create([
                {'id': i, 'guild_id': guild.id, 'enabled': default_state} for i in missing_from_db
            ])
        if missing_from_discord:
            cls.where('guild_id', guild.id).where_in('id', missing_from_discord).delete()
