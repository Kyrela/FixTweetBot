"""AddImagesboards Migration."""

from masoniteorm.migrations import Migration


class AddImageboards(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.rename("rule34", "imageboards", "boolean")
            table.boolean("imageboards").default(True).change()
            table.rename("rule34_view", "imageboards_view", "enum")
            table.table.renamed_columns["rule34_view"].values = ["normal", "direct_media"]
            table.enum("imageboards_view", ["normal", "direct_media"]).default("normal").change()
            # To the person reading this; please know that I absolutely HATE masoniteorm
            # THREE LINES OF BULLSHIT to rename a SINGLE COLUMN without changing anything else
            # HOW is this supposed to be cleared and simpler than raw SQL?
            # PLUS in order to make it work I had to check masoniteorm's source code
            # That's it I'm switch this project's ORM asap.

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.rename("imageboards", "rule34", "boolean")
            table.boolean("rule34").default(True).change()
            table.rename("imageboards_view", "rule34_view", "enum")
            table.table.renamed_columns["imageboards_view"].values = ["normal", "direct_media"]
            table.enum("rule34_view", ["normal", "direct_media"]).default("normal").change()
