"""NewEmbedezWebsites Migration."""

from masoniteorm.migrations import Migration


class NewEmbedezWebsites(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("imgur").default(False)
            table.enum("imgur_view", ["normal", "direct_media"]).default("normal").after("imgur")
            table.boolean("imgur_tr").default(False).after("imgur_view")
            table.boolean("weibo").default(True)
            table.enum("weibo_view", ["normal", "direct_media"]).default("normal").after("weibo")
            table.boolean("weibo_tr").default(False).after("weibo_view")
            table.boolean("rule34").default(True)
            table.enum("rule34_view", ["normal", "direct_media"]).default("normal").after("rule34")
            table.boolean("rule34_tr").default(False).after("rule34_view")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("imgur")
            table.drop_column("imgur_view")
            table.drop_column("imgur_tr")
            table.drop_column("weibo")
            table.drop_column("weibo_view")
            table.drop_column("weibo_tr")
            table.drop_column("rule34")
            table.drop_column("rule34_view")
            table.drop_column("rule34_tr")
