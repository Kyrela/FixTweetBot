"""ImportJson Migration."""

from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder

import json
from os import path


class ImportJson(Migration):
    def up(self):
        """
        Run the migrations.
        """

        if not path.exists('db.json'):
            return

        guilds = QueryBuilder().on(self.connection).table('guilds')
        text_channels = QueryBuilder().on(self.connection).table('text_channels')

        with open('db.json', encoding='utf-8') as f:
            data = json.load(f)

        for guild_id, guild_content in data["guilds"].items():
            guilds.create({
                "id": guild_id
            })
            for channel_id, channel_content in guild_content["channels"].items():
                text_channels.create({
                    "id": channel_id,
                    "guild_id": guild_id,
                    "fix_twitter": channel_content["fixtweet"]
                })

    def down(self):
        """
        Revert the migrations.
        """
        return

