""" CustomWebsite Model """

from typing import Optional

from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class CustomWebsite(Model):
    """CustomWebsite Model"""

    __table__ = "custom_websites"

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild

    @classmethod
    def find_or_create(cls, guild_id, website_id: int, guild_kwargs: Optional[dict] = None, **kwargs):
        website = cls.find(website_id)
        if website is None:
            from database.models.Guild import Guild
            if isinstance(guild_id, Guild):
                guild = guild_id
            else:
                guild = Guild.find_or_create(guild_id, **(guild_kwargs or {}))
            website = cls.create({'id': website_id, 'guild_id': guild.id, **kwargs}).fresh()
        return website
