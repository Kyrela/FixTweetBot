"""TwitterOption Migration."""

from masoniteorm.migrations import Migration


class TwitterOption(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('twitter').default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('twitter')
