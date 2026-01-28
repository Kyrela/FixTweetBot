"""AddNewgrounds Migration."""

from masoniteorm.migrations import Migration


class AddNewgrounds(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("newgrounds").default(True).after("deviantart")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("newgrounds")
