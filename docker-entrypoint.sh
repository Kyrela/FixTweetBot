#!/bin/bash
set -e

__config="
database:
  host: $DATABASE_HOST
  port: $DATABASE_PORT
  user: $DATABASE_USER
  password: $DATABASE_PASSWORD
  database: $DATABASE_NAME
"

echo "$__config" > /usr/local/app/database.config.yml

echo -n "Waiting for database.."
while ! nc -z $DATABASE_HOST $DATABASE_PORT 2>/dev/null; do
    echo -n "."
    sleep 1
done


echo -e \\n"Database ready"

masonite-orm migrate -C database/config.py -d database/migrations || echo "Migration failed but continuing..."

exec "$@"
