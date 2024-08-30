"""DefaultRoleState Migration."""

from masoniteorm.migrations import Migration


class DefaultRoleState(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean("default_role_state").default(True)

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column("default_role_state")
