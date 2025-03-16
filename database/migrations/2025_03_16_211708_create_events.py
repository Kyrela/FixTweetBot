"""CreateEvents Migration."""

from masoniteorm.migrations import Migration


class CreateEvents(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create("events") as table:
            table.text("name")
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop("events")
