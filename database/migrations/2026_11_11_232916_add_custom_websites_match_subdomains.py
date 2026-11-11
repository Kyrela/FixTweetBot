"""AddCustomWebsitesMatchSubdomains Migration."""

from masoniteorm.migrations import Migration


class AddCustomWebsitesMatchSubdomains(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("custom_websites") as table:
            table.boolean("match_subdomains").default(False).after("fix_domain")

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("custom_websites") as table:
            table.drop_column("match_subdomains")
