"""RefactoMembers Migration."""

from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder


class RefactoMembers(Migration):
    def up(self):
        """
        Run the migrations.
        """

        self.schema.rename("members", "old_members")

        with self.schema.table("old_members") as table:
            table.drop_foreign("members_guild_id_foreign")
            table.drop_index("members_guild_id_index")
            table.drop_unique("members_id_unique")

        with self.schema.create("members") as table:
            table.increments("id").primary().unique()

            table.big_integer("user_id").unsigned().index()

            table.big_integer("guild_id").unsigned().index()
            table.foreign("guild_id").references("id").on("guilds").on_delete("cascade")

            table.boolean("enabled").default(True)

            table.timestamps()

        old_members = QueryBuilder().on(self.connection).table('old_members')
        members = QueryBuilder().on(self.connection).table('members')

        members_to_create = [
            {
                "user_id": member["id"],
                "guild_id": member["guild_id"],
                "enabled": member["enabled"],
                "created_at": member["created_at"],
                "updated_at": member["updated_at"],
            }
            for member in old_members.all()
        ]
        members_to_create_batches = [
            members_to_create[i:i + 1000]
            for i in range(0, len(members_to_create), 1000)
        ]

        for batch in members_to_create_batches:
            members.bulk_create(batch)

        self.schema.drop("old_members")

    def down(self):
        """
        Revert the migrations.
        """

        self.schema.rename("members", "new_members")

        with self.schema.table("new_members") as table:
            table.drop_foreign("members_guild_id_foreign")
            table.drop_index("members_guild_id_index")
            table.drop_unique("members_id_unique")

        with self.schema.create("members") as table:
            table.big_integer("id").unsigned().unique()

            table.big_integer("guild_id").unsigned().index()
            table.foreign("guild_id").references("id").on("guilds").on_delete("cascade")

            table.boolean("enabled").default(True)

            table.timestamps()

        new_members = QueryBuilder().on(self.connection).table('new_members')
        members = QueryBuilder().on(self.connection).table('members')

        members_to_create = [
            {
                "id": member["user_id"],
                "guild_id": member["guild_id"],
                "enabled": member["enabled"],
                "created_at": member["created_at"],
                "updated_at": member["updated_at"],
            }
            for member in new_members.all()
        ]
        members_to_create_batches = [
            members_to_create[i:i + 1000]
            for i in range(0, len(members_to_create), 1000)
        ]

        for batch in members_to_create_batches:
            members.bulk_create(batch)

        self.schema.drop("new_members")
