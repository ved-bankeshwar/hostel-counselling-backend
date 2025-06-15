#!/bin/bash
set -e

# Use the host machine's IP address
HOST_IP="localhost"
# HOST_IP="host.docker.internal"
# export PGPASSWORD='postgres'

# Wait for PostgreSQL to become available
until psql -h "$HOST_IP" -U "postgres" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres is up - executing command"

# Check if the database exists and create it if it does not
if psql -h "$HOST_IP" -U "postgres" -tc "SELECT 1 FROM pg_database WHERE datname = 'hostel_allotment'" | grep -q 1; then
  echo "Database 'hostel_allotment' already exists."
else
  psql -h "$HOST_IP" -U "postgres" -c "CREATE DATABASE hostel_allotment"
  echo "Database 'hostel_allotment' created."
fi

# Check if the user exists and create it if it does not
if psql -h "$HOST_IP" -U "postgres" -tc "SELECT 1 FROM pg_roles WHERE rolname='admin1'" | grep -q 1; then
  echo "User 'admin1' already exists."
else
  psql -h "$HOST_IP" -U "postgres" -c "CREATE USER admin1 WITH ENCRYPTED PASSWORD '123456'"
  echo "User 'admin1' created."
fi

# Grant privileges (these commands are idempotent and can be run even if the privileges are already granted)
psql -h "$HOST_IP" -U "postgres" -d "hostel_allotment" <<-EOSQL
    GRANT ALL PRIVILEGES ON DATABASE hostel_allotment TO admin1;
    GRANT ALL ON SCHEMA public TO admin1;
    GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO admin1;
EOSQL
echo "Privileges granted to user 'admin1' on database 'hostel_allotment'."

# psql -v ON_ERROR_STOP=1 --host="$HOST_IP" --username="admin1" --dbname="unitedwayapp"

# psql -v ON_ERROR_STOP=1 --host="localhost" --username="admin1" --dbname="unitedwayapp"