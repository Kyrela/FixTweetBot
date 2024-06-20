""" TextChannel Model """

from masoniteorm.models import Model
from masoniteorm.relationships import belongs_to


class TextChannel(Model):
    """TextChannel Model"""

    __casts__ = {'fix_twitter': 'bool'}

    @belongs_to
    def guild(self):
        from database.models.Guild import Guild
        return Guild
