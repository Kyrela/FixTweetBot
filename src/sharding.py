"""Shard assignment parsing shared by the entry point and tests."""

from __future__ import annotations

import os
from collections.abc import Mapping


def shard_options(environ: Mapping[str, str] | None = None) -> dict:
    """Build validated discord.py shard options from environment variables."""

    environ = os.environ if environ is None else environ
    raw_count = environ.get('SHARD_COUNT')
    raw_ids = environ.get('SHARD_IDS')
    if not raw_count and not raw_ids:
        return {}
    if not raw_count:
        raise RuntimeError('SHARD_COUNT must be set when SHARD_IDS is configured')

    shard_count = int(raw_count)
    if shard_count < 1:
        raise ValueError('SHARD_COUNT must be greater than zero')

    options: dict = {'shard_count': shard_count}
    if raw_ids:
        shard_ids = [int(value.strip()) for value in raw_ids.split(',') if value.strip()]
        if not shard_ids:
            raise ValueError('SHARD_IDS must contain at least one shard ID')
        if len(shard_ids) != len(set(shard_ids)):
            raise ValueError('SHARD_IDS must not contain duplicates')
        if any(shard_id < 0 or shard_id >= shard_count for shard_id in shard_ids):
            raise ValueError('Every SHARD_IDS value must be within SHARD_COUNT')
        options['shard_ids'] = shard_ids
    return options
