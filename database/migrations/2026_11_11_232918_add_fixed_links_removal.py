"""AddFixedLinksRemoval Migration."""

from masoniteorm.migrations import Migration


class AddFixedLinksRemoval(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("delete_with_original").default(False).after("reply_as_original_author_replica")
            table.boolean("delete_on_reaction").default(False).after("delete_with_original")
            table.boolean("add_delete_reaction").default(False).after("delete_on_reaction")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("delete_with_original")
            table.drop_column("delete_on_reaction")
            table.drop_column("add_delete_reaction")
