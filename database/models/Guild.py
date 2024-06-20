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
        'original_message': OriginalMessage
    }

    @has_many
    def text_channels(self):
        from database.models.TextChannel import TextChannel
        return TextChannel
