"""DisableTiktokBluesky Migration."""

from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder


class DisableTiktokBluesky(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('bluesky').default(False).change()
            table.boolean('tiktok').default(False).change()

        guilds = QueryBuilder().on(self.connection).table('guilds')

        guilds.update({
            "tiktok": False,
            "bluesky": False,
        })


    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('bluesky').default(True).change()
            table.boolean('tiktok').default(True).change()

        guilds = QueryBuilder().on(self.connection).table('guilds')

        guilds.update({
            "tiktok": True,
            "bluesky": True,
        })
