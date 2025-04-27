""" Guild Model """
from enum import Enum
from typing import Self

from masoniteorm.models import Model
from masoniteorm.relationships import has_many


__all__ = ('Guild', 'OriginalMessage', 'TwitterView', 'TiktokView', 'BlueskyView')


class OriginalMessage(Enum):
    NOTHING = 'nothing'
    REMOVE_EMBEDS = 'remove_embeds'
    DELETE = 'delete'

    def get(self, value: str) -> Self:
        return self.__members__.get(value)

    def set(self, value: Self) -> str:
        return value.name


class TwitterView(Enum):
    NORMAL = 'normal'
    GALLERY = 'gallery'
    TEXT_ONLY = 'text_only'
    DIRECT_MEDIA = 'direct_media'

    def get(self, value: str) -> Self:
        return self.__members__.get(value)

    def set(self, value: Self) -> str:
        return value.name


class TiktokView(Enum):
    NORMAL = 'normal'
    GALLERY = 'gallery'
    DIRECT_MEDIA = 'direct_media'

    def get(self, value: str) -> Self:
        return self.__members__.get(value)

    def set(self, value: Self) -> str:
        return value.name

class BlueskyView(Enum):
    NORMAL = 'normal'
    DIRECT_MEDIA = 'direct_media'
    GALLERY = 'gallery'

    def get(self, value: str) -> Self:
        return self.__members__.get(value)

    def set(self, value: Self) -> str:
        return value.name


class Guild(Model):
    """Guild Model"""

    __casts__ = {
        'reply': 'bool',
        'webhooks': 'bool',
        'original_message': OriginalMessage,
        'twitter_view': TwitterView,
        'tiktok_view': TiktokView,
        'bluesky_view': BlueskyView,
        'default_channel_state': 'bool',
        'default_member_state': 'bool',
        'default_role_state': 'bool',
    }

    @has_many('id', 'guild_id')
    def text_channels(self):
        from database.models.TextChannel import TextChannel
        return TextChannel

    @has_many('id', 'guild_id')
    def members(self):
        from database.models.Member import Member
        return Member

    @has_many('id', 'guild_id')
    def custom_websites(self):
        from database.models.CustomWebsite import CustomWebsite
        return CustomWebsite

    @classmethod
    def find_or_create(cls, guild_id: int, **kwargs):
        guild = cls.find(guild_id)
        if guild is None:
            guild = cls.create({'id': guild_id, **kwargs}).fresh()
        return guild
