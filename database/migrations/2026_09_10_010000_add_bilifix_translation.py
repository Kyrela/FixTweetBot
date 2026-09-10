"""AddBilifixTranslation Migration."""

from masoniteorm.migrations import Migration


class AddBilifixTranslation(Migration):
    def up(self):
        with self.schema.table('guilds') as table:
            table.boolean('bilibili_tr').default(False).after('bilibili')

    def down(self):
        with self.schema.table('guilds') as table:
            table.drop_column('bilibili_tr')
