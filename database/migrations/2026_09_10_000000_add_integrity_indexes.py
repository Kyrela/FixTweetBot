"""AddIntegrityIndexes Migration."""

from masoniteorm.migrations import Migration
from masoniteorm.query import QueryBuilder


class AddIntegrityIndexes(Migration):
    """Deduplicate sparse settings rows and enforce their natural keys."""

    def _deduplicate(self, table_name: str, columns: list[str]) -> None:
        duplicates = (
            QueryBuilder().on(self.connection).table(table_name)
            .select(*columns)
            .group_by(','.join(columns))
            .having_raw('COUNT(*) > 1')
            .get()
        )
        for duplicate in duplicates:
            query = QueryBuilder().on(self.connection).table(table_name)
            for column in columns:
                query = query.where(column, duplicate[column])
            rows = query.select('id').order_by('id').get()
            keep_id = next(iter(rows))['id']

            delete_query = QueryBuilder().on(self.connection).table(table_name)
            for column in columns:
                delete_query = delete_query.where(column, duplicate[column])
            delete_query.where('id', '!=', keep_id).delete()

    def up(self):
        self._deduplicate('members', ['user_id', 'guild_id'])
        self._deduplicate('custom_websites', ['guild_id', 'domain'])

        with self.schema.table('members') as table:
            table.unique(
                ['user_id', 'guild_id'],
                name='members_user_id_guild_id_unique',
            )
        with self.schema.table('custom_websites') as table:
            table.unique(
                ['guild_id', 'domain'],
                name='custom_websites_guild_id_domain_unique',
            )
        with self.schema.table('events') as table:
            table.string('name', 64).change()
            table.index(
                ['name', 'created_at'],
                name='events_name_created_at_index',
            )

    def down(self):
        with self.schema.table('events') as table:
            table.drop_index('events_name_created_at_index')
            table.text('name').change()
        with self.schema.table('custom_websites') as table:
            table.drop_unique('custom_websites_guild_id_domain_unique')
        with self.schema.table('members') as table:
            table.drop_unique('members_user_id_guild_id_unique')
