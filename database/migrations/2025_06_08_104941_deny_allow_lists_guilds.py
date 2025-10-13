"""DenyAllowListsGuilds Migration."""

from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder

class DenyAllowListsGuilds(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.json("keywords").nullable().after("id")

            table.boolean("keywords_use_allow_list").index().default(False).after("keywords")
            table.boolean("text_channels_use_allow_list").index().default(False).after("keywords_use_allow_list")
            table.boolean("members_use_allow_list").index().default(False).after("text_channels_use_allow_list")
            table.boolean("roles_use_allow_list").index().default(False).after("members_use_allow_list")
            table.boolean("roles_use_any_rule").index().default(False).after("roles_use_allow_list")

        guilds = QueryBuilder().on(self.connection).table("guilds")
        guilds.where("default_channel_state", False).update({
            "text_channels_use_allow_list": True
        })
        guilds.where("default_member_state", False).update({
            "members_use_allow_list": True
        })
        guilds.where("default_role_state", False).update({
            "roles_use_allow_list": True
        })

        with self.schema.table("guilds") as table:
            table.drop_column("default_channel_state")
            table.drop_column("default_member_state")
            table.drop_column("default_role_state")

    def down(self):
        """
        Revert the migrations.
        """

        with self.schema.table("guilds") as table:
            table.boolean("default_channel_state").default(True).after("instagram")
            table.boolean("default_member_state").default(True).after("default_channel_state")
            table.boolean("default_role_state").default(True).after("default_member_state")

        guilds = QueryBuilder().on(self.connection).table("guilds")
        guilds.where("text_channels_use_allow_list", True).update({
            "default_channel_state": False
        })
        guilds.where("members_use_allow_list", True).update({
            "default_member_state": False
        })
        guilds.where("roles_use_allow_list", True).update({
            "default_role_state": False
        })

        with self.schema.table("guilds") as table:
            table.drop_column("keywords")
            table.drop_column("keywords_use_allow_list")
            table.drop_column("text_channels_use_allow_list")
            table.drop_column("members_use_allow_list")
            table.drop_column("roles_use_allow_list")
            table.drop_column("roles_use_any_rule")
