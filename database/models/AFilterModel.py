""" AFilterModel Model """
from __future__ import annotations
from typing import Optional, TYPE_CHECKING, Self

from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to

if TYPE_CHECKING:
    from database.models.Guild import Guild
    from src.utils import GuildChild

__all__ = ('AFilterModel', )

class AFilterModel(Model):
    """AFilterModel Model"""

    __table__: str

    __casts__ = {
        'on_deny_list': bool,
        'on_allow_list': bool,
    }

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild

    @classmethod
    def find_or_create(
            cls,
            d_element: GuildChild,
            guild: Optional[Guild] = None,
            guild_kwargs: Optional[dict] = None,
            **kwargs
    ) -> Self:
        """
        Find or create an element in the database.

        :param d_element: A discore element (e.g., Member, Role, TextChannel) to find or create.
        :param guild: The guild to which the element belongs. If None, it will be created or fetched.
        :param guild_kwargs: Additional keyword arguments for creating the guild if it does not exist.
        :param kwargs: Additional keyword arguments for creating the element if it does not exist.
        :return: An instance of the element if found or created, otherwise None.
        """
        element = cls.find(d_element.id)
        if element:
            return element

        if guild is None:
            from database.models.Guild import Guild
            guild = Guild.find_or_create(d_element.guild.id, **(guild_kwargs or {}))
        return cls.create({
            'id': d_element.id,
            'guild_id': guild.id,
            **kwargs
        }).fresh()

    @classmethod
    def reset_lists(cls, guild: Guild) -> None:
        """
        Reset the deny and allow lists for all elements in a guild.
        :param guild: The guild to reset the lists for.
        """
        cls.where('guild_id', guild.id).update({
            'on_allow_list': False,
            'on_deny_list': False
        })

    def enabled(self, guild: Guild = None) -> bool:
        """
        Check if the element is enabled.
        :param guild: The guild to check the element in. If None, uses the element's guild.
        :return: True if the element is enabled, False otherwise
        """

        if guild is None:
            guild = self.guild

        if guild.__getattr__(f'{self.__table__}_use_allow_list'):
            return bool(self.on_allow_list)
        else:
            return not bool(self.on_deny_list)

    def on_list(self, guild: Guild = None) -> bool:
        """
        Check if the element is on the allow or deny list.
        :param guild: The guild to check the element in. If None, uses the element's guild.
        :return: True if the element is on the allow or deny list, False otherwise
        """
        if guild is None:
            guild = self.guild

        if guild.__getattr__(f'{self.__table__}_use_allow_list'):
            return bool(self.on_allow_list)
        else:
            return bool(self.on_deny_list)

    def update_enabled(self, enabled: bool, guild: Guild = None) -> None:
        """
        Set the element's enabled status.
        :param enabled: True to enable the element, False to disable it.
        :param guild: The guild to set the element in. If None, uses the element's guild.
        """
        if guild is None:
            guild = self.guild

        if guild.__getattr__(f'{self.__table__}_use_allow_list'):
            self.update({'on_allow_list': enabled})
        else:
            self.update({'on_deny_list': not enabled})
