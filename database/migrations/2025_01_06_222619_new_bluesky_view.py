"""NewBlueskyView Migration."""

from masoniteorm.migrations import Migration


class NewBlueskyView(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum('bluesky_view', ['normal', 'direct_media', 'gallery']).default('normal').change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum('bluesky_view', ['normal', 'direct_media']).default('normal').change()
