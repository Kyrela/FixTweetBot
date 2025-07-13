""" DiscordRepresentation Model """
from __future__ import annotations
from typing import TYPE_CHECKING, Self

import discore
from masoniteorm.models import Model

if TYPE_CHECKING:
    from database.models.Guild import Guild

__all__ = ('DiscordRepresentation', )

class DiscordRepresentation(Model):
    """DiscordRepresentation Model"""

    __table__: str

    @classmethod
    def find_or_create(
            cls,
            d_element: discore.Object,
            **kwargs
    ) -> Self:
        """
        Find or create an element in the database.

        :param d_element: A discore element to find or create.
        :param kwargs: Additional keyword arguments for creating the element if it does not exist.
        :return: An instance of the element if found or created, otherwise None.
        """
        element = cls.find(d_element.id)
        if element:
            return element

        return cls.create({
            'id': d_element.id,
            **kwargs
        }).fresh()
