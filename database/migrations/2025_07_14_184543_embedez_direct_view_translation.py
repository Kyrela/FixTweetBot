"""EmbedezDirectViewTranslation Migration."""

from masoniteorm.migrations import Migration


class EmbedezDirectViewTranslation(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.rename("twitter_tr_lang", "lang", "string", 255)
            table.string("lang").nullable().after("roles_use_any_rule").change()
            table.enum("instagram_view", ["normal", "direct_media"]).default("normal").after("instagram")
            table.boolean("instagram_tr").default(False).after("instagram_view")
            table.enum("snapchat_view", ["normal", "direct_media"]).default("normal").after("snapchat")
            table.boolean("snapchat_tr").default(False).after("snapchat_view")
            table.enum("ifunny_view", ["normal", "direct_media"]).default("normal").after("ifunny")
            table.boolean("ifunny_tr").default(False).after("ifunny_view")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.rename("lang", "twitter_tr_lang", "string", 255)
            table.string("twitter_tr_lang").nullable().change()
            table.drop_column("instagram_view")
            table.drop_column("instagram_tr")
            table.drop_column("snapchat_view")
            table.drop_column("snapchat_tr")
            table.drop_column("ifunny_view")
            table.drop_column("ifunny_tr")
