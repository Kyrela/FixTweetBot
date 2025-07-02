"""DenyAllowListsMembers Migration."""

from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder


class DenyAllowListsMembers(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("members") as table:
            table.boolean("on_deny_list").after("guild_id").index().default(False)
            table.boolean("on_allow_list").after("on_deny_list").index().default(False)

        members = QueryBuilder().on(self.connection).table("members")
        guilds = QueryBuilder().on(self.connection).table("guilds")

        guilds_using_allow_list_ids = [g['id'] for g in guilds.where("members_use_allow_list", True).get()]

        if guilds_using_allow_list_ids:
            members.where("enabled", False).where_not_in("guild_id", guilds_using_allow_list_ids).update({
                "on_deny_list": True
            })

            members.where("enabled", True).where_in("guild_id", guilds_using_allow_list_ids).update({
                "on_allow_list": True
            })
        else:
            members.where("enabled", False).update({
                "on_deny_list": True
            })

        with self.schema.table("members") as table:
            table.drop_column("enabled")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("members") as table:
            table.boolean("enabled").after("guild_id").default(True)

        members = QueryBuilder().on(self.connection).table("members")
        guilds = QueryBuilder().on(self.connection).table("guilds")

        guilds_using_allow_list_ids = [g['id'] for g in guilds.where("members_use_allow_list", True).get()]

        if guilds_using_allow_list_ids:
            members.where("on_deny_list", True).where_not_in("guild_id", guilds_using_allow_list_ids).update({
                "enabled": False
            })

            members.where("on_allow_list", False).where_in("guild_id", guilds_using_allow_list_ids).update({
                "enabled": False
            })
        else:
            members.where("on_deny_list", True).update({
                "enabled": False
            })

        with self.schema.table("members") as table:
            table.drop_column("on_deny_list")
            table.drop_column("on_allow_list")
