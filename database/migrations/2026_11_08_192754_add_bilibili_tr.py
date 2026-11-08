"""AddBilibiliTr Migration."""

from masoniteorm.migrations import Migration


class AddBilibiliTr(Migration):
    def up(self):
        """
        Run the migrations.
        """
        with self.schema.table("guilds") as table:
            table.boolean('bilibili_tr').default(False).after('bilibili')

    def down(self):
        """
        Revert the migrations.
        """
        with self.schema.table("guilds") as table:
            table.drop_column('bilibili_tr')
