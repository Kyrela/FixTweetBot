"""CustomWebsitesTable Migration."""

from masoniteorm.migrations import Migration


class CustomWebsitesTable(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("custom_websites") as table:
            table.increments("id")

            table.big_integer("guild_id").unsigned().index()
            table.foreign("guild_id").references("id").on("guilds").on_delete("cascade")

            table.string("name")
            table.string("domain")
            table.string("fix_domain")

            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("custom_websites")
