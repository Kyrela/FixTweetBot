""" Event Model """

from masoniteorm.models import Model
from typing import Self
import datetime as dt


class Event(Model):
    """Event Model"""

    @classmethod
    def since(cls, days: int = 1, hours: int = 0, minutes: int = 0, seconds: int = 0) -> list[Self]:
        """
        Get all events since a certain time

        :param days: the number of days
        :param hours: the number of hours
        :param minutes: the number of minutes
        :param seconds: the number of seconds

        :return: the events since the time
        """

        return cls.where('created_at', '>=', dt.datetime.now() - dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)).get()
