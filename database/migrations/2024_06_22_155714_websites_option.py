"""WebsitesOption Migration."""

from masoniteorm.migrations import Migration


class WebsitesOption(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('twitter').default(True)
            table.boolean('twitter_tr').default(False)
            table.string('twitter_tr_lang').nullable()
            table.boolean('instagram').default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('twitter')
            table.drop_column('twitter_tr')
            table.drop_column('twitter_tr_lang')
            table.drop_column('instagram')
