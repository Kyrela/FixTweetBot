"""RemoveInstagramViews Migration."""

from masoniteorm.migrations import Migration


class RemoveInstagramView(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("instagram_view")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("instagram_view", ["normal", "gallery", "direct_media"]).default("normal")
