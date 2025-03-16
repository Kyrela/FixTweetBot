"""AddMoreWebsites Migration."""

from masoniteorm.migrations import Migration


class AddTwitchSpotify(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('twitch').default(True)
            table.boolean('spotify').default(False)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('twitch')
            table.drop_column('spotify')
