"""MembersTable Migration."""

from masoniteorm.migrations import Migration


class MembersTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("members") as table:
            table.big_integer("id").unsigned().unique()

            table.big_integer("guild_id").unsigned().index()
            table.foreign("guild_id").references("id").on("guilds").on_delete("cascade")

            table.boolean("enabled").default(True)

            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("members")
