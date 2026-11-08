"""AddLinkedin Migration."""

from masoniteorm.migrations import Migration


class AddLinkedin(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("linkedin").default(True).after("imgur")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("linkedin")
