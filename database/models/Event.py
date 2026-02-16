""" Event Model """

import asyncio
from typing import Self
import datetime as dt
import json

from masoniteorm.models import Model

import discore

class Event(Model):
    """Event Model"""

    __table__ = "events"
    _buffer = []
    _flush_task: asyncio.Task | None = None
    _lock: asyncio.Lock = asyncio.Lock()

    @classmethod
    def since(cls, event_name: str | None = None, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0) -> list[Self]:
        """
        Get the events since a certain time, with an optional filter by event name.
        If the time is 0, get all the events.

        :param event_name: the name of the event to filter by
        :param days: the number of days
        :param hours: the number of hours
        :param minutes: the number of minutes
        :param seconds: the number of seconds

        :return: the events since the time
        """

        if not discore.config.analytic:
            return []

        query = cls.where('name', event_name) if event_name else cls

        delta = dt.timedelta(days=days, hours=hours, minutes=minutes, seconds=seconds)
        if delta:
            query = query.where('created_at', '>=', dt.datetime.now() - delta)

        return query.get()

    @classmethod
    async def _flush_loop(cls) -> None:
        """
        Flush the buffer every 5 seconds
        :return: None
        """
        while True:
            await asyncio.sleep(5)
            async with cls._lock:
                if cls._buffer:
                    cls.bulk_create(cls._buffer)
                    cls._buffer.clear()

    @classmethod
    async def buff_cr(cls, event=None) -> None:
        """
        Buffer the creation of an event, and flush it every 5 seconds
        
        :param event: the event to create, in the form of a dictionary.
        :return: None
        """
        if not discore.config.analytic:
            return
        if 'data' in event and not isinstance(event['data'], str):
            event['data'] = json.dumps(event['data'])
        async with cls._lock:
            cls._buffer.append(event)

        if cls._flush_task is None or cls._flush_task.done():
            cls._flush_task = asyncio.create_task(cls._flush_loop())
