"""AddSnapchat Migration."""

from masoniteorm.migrations import Migration


class AddSnapchat(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('snapchat').default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('snapchat')
