"""GuildSettings Migration."""

from masoniteorm.migrations import Migration


class GuildSettings(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.enum("original_message", ["nothing", "remove_embeds", "delete"]).default("remove_embeds")
            table.boolean("reply").default(False)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("original_message")
            table.drop_column("reply")
