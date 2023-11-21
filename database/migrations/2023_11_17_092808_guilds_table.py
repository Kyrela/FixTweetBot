"""GuildsTable Migration."""

from masoniteorm.migrations import Migration


class GuildsTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("guilds") as table:
            table.big_integer("id").unsigned().unique()

            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("guilds")
