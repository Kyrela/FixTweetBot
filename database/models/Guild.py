""" Guild Model """
from enum import Enum
from typing import Self

from masoniteorm.models import Model
from masoniteorm.relationships import has_many


__all__ = ('Guild', 'OriginalMessage')


class OriginalMessage(Enum):
    NOTHING = 'nothing'
    REMOVE_EMBEDS = 'remove_embeds'
    DELETE = 'delete'

    def get(self, value: str) -> Self:
        return self.__members__.get(value)

    def set(self, value: Self) -> str:
        return value.name


class Guild(Model):
    """Guild Model"""

    __casts__ = {
        'reply': 'bool',
        'original_message': OriginalMessage,
        'twitter': 'bool',
        'twitter_tr': 'bool',
        'instagram': 'bool',
    }

    @has_many
    def text_channels(self):
        from database.models.TextChannel import TextChannel
        return TextChannel

    @has_many
    def members(self):
        from database.models.Member import Member
        return Member

    @classmethod
    def find_or_create(cls, guild_id: int, **kwargs):
        guild = cls.find(guild_id)
        if guild is None:
            guild = cls.create({'id': guild_id, **kwargs}).fresh()
        return guild
