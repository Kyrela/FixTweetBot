""" Event Model """

import asyncio
from typing import Self
import datetime as dt
import json
import logging
import os

from masoniteorm.models import Model

import discore


_logger = logging.getLogger(__name__)
_buffer_limit = max(1000, int(os.getenv('ANALYTICS_BUFFER_LIMIT', '100000')))
_flush_batch_size = max(100, int(os.getenv('ANALYTICS_FLUSH_BATCH_SIZE', '5000')))

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
    def count_since(cls, event_name: str | None = None, **delta_kwargs) -> int:
        """Count matching events in the database without materialising model objects."""

        if not discore.config.analytic:
            return 0
        query = cls.where('name', event_name) if event_name else cls
        delta = dt.timedelta(**delta_kwargs)
        if delta:
            query = query.where('created_at', '>=', dt.datetime.now() - delta)
        return query.count()

    @classmethod
    async def _flush_loop(cls) -> None:
        """Flush the buffer every 5 seconds"""
        while True:
            await asyncio.sleep(5)
            async with cls._lock:
                if cls._buffer:
                    events = cls._buffer[:_flush_batch_size]
                    del cls._buffer[:_flush_batch_size]
                else:
                    continue
            try:
                await asyncio.to_thread(cls.bulk_create, events)
            except Exception:
                _logger.exception('Failed to flush analytics events')
                async with cls._lock:
                    cls._buffer = (events + cls._buffer)[-_buffer_limit:]

    @classmethod
    async def buff_cr(cls, *events: dict) -> None:
        """
        Buffer the creation of events, and flush them every 5 seconds.

        :param events: the events to create, each event is a dict with the keys 'name', 'data' and optionally 'created_at'
        """
        if not discore.config.analytic:
            return
        events = list(events)
        for i, event in enumerate(events):
            if 'data' in event and not isinstance(event['data'], str):
                event['data'] = json.dumps(event['data'])
            if not 'name' in event:
                raise ValueError("Event must have a name")
            if not 'data' in event:
                event['data'] = '{}'
            event['created_at'] = dt.datetime.now() if not 'created_at' in event else event['created_at']
            events[i] = event
        async with cls._lock:
            cls._buffer.extend(events)
            if len(cls._buffer) > _buffer_limit:
                del cls._buffer[:-_buffer_limit]

        if cls._flush_task is None or cls._flush_task.done():
            cls._flush_task = asyncio.create_task(cls._flush_loop())
