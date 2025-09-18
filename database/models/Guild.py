""" Guild Model """
import discore

from enum import Enum
from typing import Self

from masoniteorm.models import Model
from masoniteorm.relationships import has_many


__all__ = ('Guild', 'OriginalMessage', 'TwitterView', 'InstagramView', 'TiktokView', 'BlueskyView', 'EmbedEzView')

from database.models.DiscordRepresentation import DiscordRepresentation


class GettableEnum(Enum):
    def get(self, value: str) -> Self:
        return self.__members__.get(value)

    def set(self, value: Self) -> str:
        return value.name


class OriginalMessage(GettableEnum):
    NOTHING = 'nothing'
    REMOVE_EMBEDS = 'remove_embeds'
    DELETE = 'delete'


class TwitterView(GettableEnum):
    NORMAL = 'normal'
    GALLERY = 'gallery'
    TEXT_ONLY = 'text_only'
    DIRECT_MEDIA = 'direct_media'

class InstagramView(GettableEnum):
    NORMAL = 'normal'
    DIRECT_MEDIA = 'direct_media'

class TiktokView(GettableEnum):
    NORMAL = 'normal'
    GALLERY = 'gallery'
    DIRECT_MEDIA = 'direct_media'

class BlueskyView(GettableEnum):
    NORMAL = 'normal'
    DIRECT_MEDIA = 'direct_media'
    GALLERY = 'gallery'

class EmbedEzView(GettableEnum):
    NORMAL = 'normal'
    DIRECT_MEDIA = 'direct_media'


class Guild(DiscordRepresentation):
    """Guild Model"""

    __table__ = "guilds"

    __casts__ = {
        'keywords': 'json',
        'keywords_use_allow_list': bool,
        'text_channels_use_allow_list': bool,
        'members_use_allow_list': bool,
        'roles_use_allow_list': bool,
        'roles_use_any_rule': bool,
        'reply_to_message': bool,
        'reply_silently': bool,
        'webhooks': bool,
        'original_message': OriginalMessage,
        'twitter_view': TwitterView,
        'tiktok_view': TiktokView,
        'bluesky_view': BlueskyView,
        'instagram_view': InstagramView,
        'snapchat_view': EmbedEzView,
        'ifunny_view': EmbedEzView,
        'imgur_view': EmbedEzView,
        'weibo_view': EmbedEzView,
        'rule34_view': EmbedEzView,
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
    def find_or_create(cls, d_guild: discore.Guild, **kwargs):
        guild = cls.find(d_guild.id)
        if guild is None:
            guild = cls.create({'id': d_guild.id, **kwargs}).fresh()
        return guild
