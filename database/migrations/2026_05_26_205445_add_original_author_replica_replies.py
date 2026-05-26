"""AddOriginalAuthorReplicaReplies Migration."""

from masoniteorm.migrations import Migration


class AddOriginalAuthorReplicaReplies(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("reply_as_original_author_replica").after("reply_silently").default(False)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("reply_as_original_author_replica")
