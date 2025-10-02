#!/bin/bash
set -e

echo "Starting SQL Server for CDC setup..."

# Start SQL Server and Kafka
docker compose -f docker-compose.test.yml up -d sqlserver kafka

# Wait for SQL Server to be healthy
echo "Waiting for SQL Server to be ready..."
timeout=60
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose -f docker-compose.test.yml exec -T sqlserver /opt/mssql-tools18/bin/sqlcmd -S localhost -U sa -P TestPass123! -C -Q "SELECT 1" > /dev/null 2>&1; then
        echo "SQL Server is ready"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "ERROR: SQL Server failed to become ready within ${timeout}s"
    exit 1
fi

# Wait for Kafka to be healthy
echo "Waiting for Kafka to be ready..."
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose -f docker-compose.test.yml exec -T kafka rpk cluster health 2>/dev/null | grep -q "Healthy.*true"; then
        echo "Kafka is ready"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "ERROR: Kafka failed to become ready within ${timeout}s"
    exit 1
fi

# Get the network name from running containers
FULL_NETWORK=$(docker compose -f docker-compose.test.yml ps --format json | grep -o '"Networks":"[^"]*"' | head -1 | cut -d'"' -f4)

# Install pymssql and run setup
echo "Enabling CDC on SQL Server (network: ${FULL_NETWORK})..."
docker run --rm \
    --network "${FULL_NETWORK}" \
    -v "$(pwd)/setup_sqlserver.py:/setup.py:ro" \
    -e SQL_HOST=sqlserver \
    -e SQL_PORT=1433 \
    -e SQL_USER=sa \
    -e SQL_PASSWORD=TestPass123! \
    -e SQL_DATABASE=testdb \
    -e SQL_SCHEMA=dbo \
    -e SQL_TABLE=test_table \
    python:3.11-slim \
    bash -c "pip install pymssql > /dev/null 2>&1 && python /setup.py"

echo "CDC setup complete!"
