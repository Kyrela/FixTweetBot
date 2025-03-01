"""AddMoreWebsites Migration."""

from masoniteorm.migrations import Migration


class AddMoreWebsites(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('mastodon').default(False)
            table.boolean('deviantart').default(True)
            table.boolean('tumblr').default(False)
            table.boolean('facebook').default(True)
            table.boolean('bilibili').default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('mastodon')
            table.drop_column('deviantart')
            table.drop_column('tumblr')
            table.drop_column('facebook')
            table.drop_column('bilibili')
