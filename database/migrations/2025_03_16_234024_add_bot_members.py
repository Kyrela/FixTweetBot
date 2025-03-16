"""AddBotMembers Migration."""

from masoniteorm.migrations import Migration


class AddBotMembers(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("members") as table:
            table.boolean("bot").default(False)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("members") as table:
            table.drop_column("bot")
