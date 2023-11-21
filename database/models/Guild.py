""" Guild Model """

from masoniteorm.models import Model
from masoniteorm.relationships import has_many


class Guild(Model):
    """Guild Model"""

    @has_many
    def text_channels(self):
        from database.models.TextChannel import TextChannel
        return TextChannel
