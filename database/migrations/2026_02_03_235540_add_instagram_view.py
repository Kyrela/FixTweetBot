"""AddInstagramView Migration."""

from masoniteorm.migrations import Migration


class AddInstagramView(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("instagram_view", ['normal', 'direct_media', 'gallery']).default("normal").change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("instagram_view", ['normal', 'direct_media']).default("normal").change()
