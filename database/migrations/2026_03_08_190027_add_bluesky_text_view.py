"""AddBlueskyTextView Migration."""

from masoniteorm.migrations import Migration


class AddBlueskyTextView(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("bluesky_view", ["normal", "gallery", "text_only", "direct_media"]).default("normal").change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("bluesky_view", ["normal", "gallery", "direct_media"]).default("normal").change()
