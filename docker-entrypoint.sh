#!/bin/sh
set -e

python - <<'PY'
import json
import os
from pathlib import Path

config = {
    'database': {
        'host': os.environ['DATABASE_HOST'],
        'port': int(os.environ['DATABASE_PORT']),
        'user': os.environ['DATABASE_USER'],
        'driver': os.environ['DATABASE_DRIVER'],
        'password': os.environ['DATABASE_PASSWORD'],
        'database': os.environ['DATABASE_NAME'],
    },
    'token': os.environ.get('DISCORD_TOKEN', ''),
}
if os.environ.get('DEV_GUILD'):
    config['dev_guild'] = int(os.environ['DEV_GUILD'])

path = Path('/usr/local/app/docker.config.yml')
path.write_text(json.dumps(config), encoding='utf-8')
path.chmod(0o600)
PY

echo -n "Waiting for database.."
waited=0
wait_timeout="${DATABASE_WAIT_TIMEOUT:-120}"
while ! nc -z $DATABASE_HOST $DATABASE_PORT 2>/dev/null; do
    echo -n "."
    sleep 1
    waited=$((waited + 1))
    if [ "$waited" -ge "$wait_timeout" ]; then
        echo " database wait timed out"
        exit 1
    fi
done


echo -e \\n"Database ready"

if [ "${RUN_DATABASE_MIGRATIONS:-false}" = "true" ]; then
    masonite-orm migrate -C database/config.py -d database/migrations
fi

exec "$@"
