"""AddBlueskyView Migration."""

from masoniteorm.migrations import Migration


class AddBlueskyView(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum('bluesky_view', ['normal', 'direct_media']).default('normal')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('bluesky_view')
