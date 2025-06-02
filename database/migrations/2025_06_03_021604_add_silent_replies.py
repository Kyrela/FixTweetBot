"""AddSilentReplies Migration."""

from masoniteorm.migrations import Migration


class AddSilentReplies(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.rename("reply", "reply_to_message", "boolean")
            table.boolean("reply_to_message").default(False).change()
            table.boolean("reply_silently").after("reply").default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.rename("reply_to_message", "reply", "boolean")
            table.boolean("reply").default(False).change()
            table.drop_column("reply_silently")
