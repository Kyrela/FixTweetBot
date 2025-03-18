"""AddWebhookSupport Migration."""

from masoniteorm.migrations import Migration


class AddWebhookSupport(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("webhooks").default(False)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("webhooks")
