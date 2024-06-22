"""ChannelsEnabled Migration."""

from masoniteorm.migrations import Migration


class ChannelsEnabled(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("text_channels") as table:
            table.rename('fix_twitter', 'enabled', 'boolean')
            table.boolean('enabled').default(True).change()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("text_channels") as table:
            table.rename('enabled', 'fix_twitter', 'boolean')
            table.boolean('fix_twitter').default(True).change()
