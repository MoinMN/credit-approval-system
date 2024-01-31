#!/bin/sh

# wait-for-db.sh
# Wait until the database is ready to accept connections.

set -e

host="$1"
shift
cmd="$@"

until PGPASSWORD=$POSTGRES_PASSWORD psql -h db -U $POSTGRES_USER -d $POSTGRES_DB -c '\q'; do
    echo "Postgres is unavailable - sleeping"
    sleep 1
done


>&2 echo "Postgres is up - executing command"
exec $cmd
