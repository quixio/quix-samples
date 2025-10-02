#!/bin/bash
set -e

echo "Starting TDengine and Kafka for setup..."

# Start TDengine and Kafka
docker compose -f docker-compose.test.yml up -d tdengine kafka

# Wait for TDengine to be healthy
echo "Waiting for TDengine to be ready..."
timeout=90
elapsed=0
while [ $elapsed -lt $timeout ]; do
    if docker compose -f docker-compose.test.yml exec -T tdengine taos -s 'show databases;' > /dev/null 2>&1; then
        echo "TDengine is ready"
        break
    fi
    sleep 2
    elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
    echo "ERROR: TDengine failed to become ready within ${timeout}s"
    exit 1
fi

# Wait for Kafka to be healthy
echo "Waiting for Kafka to be ready..."
elapsed=0
timeout=60
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

# Install TDengine client and run setup
echo "Creating TDengine database and supertable..."
docker run --rm \
    --network tdengine_test-network \
    -v "$(pwd)/setup_tdengine.py:/setup.py:ro" \
    python:3.11-slim \
    bash -c "pip install taospy requests > /dev/null 2>&1 && python /setup.py"

echo "TDengine setup complete!"
