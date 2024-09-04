"""WebsitesAndViews Migration."""

from masoniteorm.migrations import Migration


class WebsitesAndViews(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("instagram_view", ["normal", "gallery", "direct_media"]).default("normal")
            table.enum("twitter_view", ["normal", "gallery", "text_only", "direct_media"]).default("normal")
            table.boolean('tiktok').default(True)
            table.enum('tiktok_view', ['normal', 'gallery', 'direct_media']).default('normal')
            table.boolean('reddit').default(True)
            table.boolean('threads').default(True)
            table.boolean('bluesky').default(True)
            table.boolean('pixiv').default(True)
            table.boolean('ifunny').default(True)
            table.boolean('furaffinity').default(True)
            table.boolean('youtube').default(False)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("instagram_view")
            table.drop_column("twitter_view")
            table.drop_column("tiktok")
            table.drop_column("tiktok_view")
            table.drop_column("reddit")
            table.drop_column("threads")
            table.drop_column("bluesky")
            table.drop_column("pixiv")
            table.drop_column("ifunny")
            table.drop_column("furaffinity")
            table.drop_column("youtube")
