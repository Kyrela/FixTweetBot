"""AddEventsData Migration."""

from masoniteorm.migrations import Migration


class AddEventsData(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("events") as table:
            table.json('data').default('{}').after('name')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("events") as table:
            table.drop_column("data")
