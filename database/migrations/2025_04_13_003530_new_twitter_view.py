"""NewTwitterView Migration."""

from masoniteorm.migrations import Migration


class NewTwitterView(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum('twitter_view', ['normal', 'gallery', 'text_only', 'direct_media', 'compatibility']).default('normal').change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum('twitter_view', ['normal', 'gallery', 'text_only', 'direct_media']).default('normal').change()
