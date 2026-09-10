"""AddXiaohongshu Migration."""

from masoniteorm.migrations import Migration


class AddXiaohongshu(Migration):
    def up(self):
        """Add Xiaohongshu website settings."""
        with self.schema.table("guilds") as table:
            table.boolean("xiaohongshu").default(True)

    def down(self):
        """Remove Xiaohongshu website settings."""
        with self.schema.table("guilds") as table:
            table.drop_column("xiaohongshu")
