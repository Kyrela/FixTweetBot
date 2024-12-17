"""DefaultStates Migration."""

from masoniteorm.migrations import Migration


class DefaultStates(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("default_channel_state").default(True)
            table.boolean("default_member_state").default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("default_channel_state")
            table.drop_column("default_member_state")
