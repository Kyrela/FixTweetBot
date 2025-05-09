#!/bin/bash
set -e

__config="
database:
  host: $DATABASE_HOST
  port: $DATABASE_PORT
  user: $DATABASE_USER
  driver: $DATABASE_DRIVER
  password: $DATABASE_PASSWORD
  database: $DATABASE_NAME

token: $DISCORD_TOKEN
dev_guild: $DEV_GUILD
"

echo "$__config" > /usr/local/app/docker.config.yml

echo -n "Waiting for database.."
while ! nc -z $DATABASE_HOST $DATABASE_PORT 2>/dev/null; do
    echo -n "."
    sleep 1
done


echo -e \\n"Database ready"

masonite-orm migrate -C database/config.py -d database/migrations || echo "Migration failed but continuing..."

exec "$@"
