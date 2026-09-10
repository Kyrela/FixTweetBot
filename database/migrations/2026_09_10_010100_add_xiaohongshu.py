"""AddXiaohongshu Migration."""

from masoniteorm.migrations import Migration


class AddXiaohongshu(Migration):
    def up(self):
        """Add Xiaohongshu website settings."""
        with self.schema.table("guilds") as table:
            table.boolean("xiaohongshu").default(True)
            table.enum("xiaohongshu_view", ["normal", "direct_media"]).default("normal").after("xiaohongshu")
            table.boolean("xiaohongshu_tr").default(False).after("xiaohongshu_view")

    def down(self):
        """Remove Xiaohongshu website settings."""
        with self.schema.table("guilds") as table:
            table.drop_column("xiaohongshu")
            table.drop_column("xiaohongshu_view")
            table.drop_column("xiaohongshu_tr")
