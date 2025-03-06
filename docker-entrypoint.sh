#!/bin/bash
set -e

while ! nc -z $DATABASE_HOST $DATABASE_PORT 2>/dev/null; do
    echo "Waiting for database..."
    sleep 1
done

echo "Database ready"

masonite-orm migrate -C database/config.py -d database/migrations || echo "Migration failed but continuing..."

exec "$@"
