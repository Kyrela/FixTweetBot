"""Add link render template Migration."""

from masoniteorm.migrations import Migration


class AddLinkRenderTemplate(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.text("link_render_template").nullable()

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("link_render_template")