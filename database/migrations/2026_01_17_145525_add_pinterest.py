"""AddPinterest Migration."""

from masoniteorm.migrations import Migration


class AddPinterest(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("pinterest").default(True)
            table.enum("pinterest_view", ["normal", "direct_media"]).default("normal").after("pinterest")
            table.boolean("pinterest_tr").default(False).after("pinterest_view")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("pinterest")
            table.drop_column("pinterest_view")
            table.drop_column("pinterest_tr")
