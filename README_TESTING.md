# QuixStreams Samples - Testing Guide

## Prerequisites

**Required:**
- Docker Desktop (or Docker Engine + Docker Compose)
- bash (you already have it!)

**That's it!** No Make, no Python, no dependencies - just Docker!

---

## Quick Start (30 seconds)

```bash
./test.sh start-kafka    # Start infrastructure
./test.sh test-csv       # Run CSV test
./test.sh stop           # Stop everything
```

All commands available:
```bash
./test.sh help           # Show all commands
```

---

## Structure

```
/
├── test.sh                       ← Main test runner (bash + docker)
├── tests/                        ← All tests here (NOT in samples!)
│   ├── sources/
│   │   └── simple_csv/
│   │       └── test_csv_source.py
│   └── destinations/
│       └── postgres/
│           └── test_postgres_sink.py
├── test-framework/               ← Shared test utilities
│   └── __init__.py
├── test-infrastructure/          ← Docker services
│   ├── docker-compose.yml
│   └── scripts/
└── python/sources/simple_csv/    ← Clean sample (no tests!)
    ├── library.json
    ├── main.py
    └── requirements.txt
```

**Why This Structure?**

✅ **Samples stay clean** - No test contamination
✅ **Tests are separate** - In `/tests/` directory
✅ **Zero dependencies** - Only Docker required
✅ **Pure bash** - No Make, works everywhere

---

## Full Test Workflow

### Running Tests

**Single app:**
```bash
./test.sh test-csv
```

**By category:**
```bash
./test.sh test-sources         # All source tests
./test.sh test-destinations    # All destination tests
./test.sh test-transformations # All transformation tests
```

**All tests:**
```bash
./test.sh test-all
```

**Interactive debugging:**
```bash
./test.sh test-shell
# Now you're in container with all deps
pytest tests/sources/simple_csv/ -vv -s
```

### Managing Services

**Start services:**
```bash
./test.sh start-kafka         # Kafka only
./test.sh start-postgres      # Kafka + PostgreSQL
./test.sh start-mongodb       # Kafka + MongoDB
./test.sh start-redis         # Kafka + Redis
./test.sh start-all           # Everything
```

**Stop services:**
```bash
./test.sh stop                # Stop all (keep data)
./test.sh clean               # Stop + delete volumes
```

**Debug services:**
```bash
./test.sh status              # Show running containers
./test.sh kafka-ui            # Open Kafka UI
./test.sh logs kafka          # Show service logs
```

---

## How It Works

### Test Runner Container

All Python dependencies live in a Docker container (`quix-test-runner`):

```
┌─────────────────────────────────────┐
│  quix-test-runner container         │
│                                     │
│  - Python 3.11                      │
│  - pytest                           │
│  - confluent-kafka                  │
│  - psycopg2 (PostgreSQL)            │
│  - pymongo (MongoDB)                │
│  - redis                            │
│  - All test dependencies            │
│                                     │
│  Your code mounted at /workspace    │
└─────────────────────────────────────┘
```

### Test Execution Flow

```bash
# On your machine (only Docker required)
./test.sh test-csv

# What happens:
1. Starts Kafka container (if not running)
2. Builds test-runner container (if not built)
3. Starts test-runner container (if not running)
4. Runs inside container:
   docker exec quix-test-runner pytest tests/sources/simple_csv/ -v

# Tests run inside container with access to:
- Kafka broker (kafka:9092)
- Your source code (/workspace)
- All Python dependencies (pre-installed)
```

---

## Running Tests

### Single App Test
```bash
./test.sh test-csv
```

### Test Categories
```bash
./test.sh test-sources         # All source tests
./test.sh test-destinations    # All destination tests
./test.sh test-transformations # All transformation tests
```

### All Tests
```bash
./test.sh test-all
```

### Quick Check
```bash
./test.sh start-kafka
./test.sh test-csv
./test.sh stop
```

---

## Interactive Testing

### Open Shell in Test Container
```bash
./test.sh test-shell
```

This drops you into the test container where you can:
```bash
# You're now in the container with all dependencies
pytest tests/sources/simple_csv/ -v
pytest tests/sources/simple_csv/ -vv -s
pytest tests/sources/simple_csv/ -k "test_csv_publishes"

# Or run apps directly
cd python/sources/simple_csv
export output=test-topic
export Quix__Broker__Address=kafka:9092
python main.py

# Or explore
python
>>> from confluent_kafka import Producer
>>> # All dependencies available
```

---

## Writing New Tests

### 1. Create Test File

`tests/sources/my_app/test_my_app.py`:

```python
"""Tests for My App"""
import pytest
import time
import os
import subprocess
import json
from pathlib import Path
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic


class TestMyApp:
    @pytest.fixture
    def kafka_broker(self):
        return "kafka:9092"  # Internal Docker network

    @pytest.fixture
    def test_topic(self):
        return f"test-my-app-{int(time.time())}"

    def test_my_app_works(self, kafka_broker, test_topic):
        """Test that my app does what it should"""

        # 1. Create Kafka topic
        admin = AdminClient({"bootstrap.servers": kafka_broker})
        topic = NewTopic(test_topic, num_partitions=1, replication_factor=1)
        admin.create_topics([topic])

        # 2. Run your app
        env = os.environ.copy()
        env["output"] = test_topic
        env["Quix__Broker__Address"] = kafka_broker

        process = subprocess.Popen(
            ["python", "main.py"],
            cwd="/workspace/python/sources/my_app",
            env=env,
        )

        time.sleep(10)  # Let it run
        process.terminate()
        process.wait()

        # 3. Verify results
        consumer = Consumer({
            "bootstrap.servers": kafka_broker,
            "group.id": "test",
            "auto.offset.reset": "earliest",
        })
        consumer.subscribe([test_topic])

        messages = []
        for _ in range(10):
            msg = consumer.poll(timeout=5.0)
            if msg and not msg.error():
                messages.append(msg)

        consumer.close()

        # 4. Assertions
        assert len(messages) > 0, "Should publish messages"

        # Cleanup
        admin.delete_topics([test_topic])
```

### 2. Run It
```bash
# From your host machine
./test.sh test-shell

# Inside container
pytest tests/sources/my_app/test_my_app.py -v
```

Or directly:
```bash
docker exec quix-test-runner pytest tests/sources/my_app/test_my_app.py -v
```

---

## Available Test Helpers

### Inside Test Container

All these are available in your tests:

```python
# Kafka
from confluent_kafka import Producer, Consumer, KafkaError
from confluent_kafka.admin import AdminClient, NewTopic

# PostgreSQL
import psycopg2

# MongoDB
import pymongo

# Redis
import redis

# Testing
import pytest

# Utilities
import subprocess  # Run apps
import json        # Parse messages
import time        # Timing/delays
```

---

## Infrastructure Commands

### Start Services

```bash
./test.sh start-kafka         # Kafka only
./test.sh start-postgres      # Kafka + PostgreSQL
./test.sh start-mongodb       # Kafka + MongoDB
./test.sh start-redis         # Kafka + Redis
./test.sh start-all           # Everything
```

### Stop Services

```bash
./test.sh stop               # Stop all (keep data)
./test.sh clean              # Stop + delete volumes
```

### Rebuild Test Container

If you change dependencies:

```bash
./test.sh build
```

### Debug

```bash
./test.sh status             # Show running containers
./test.sh kafka-ui           # Open Kafka UI
./test.sh test-shell         # Interactive shell in test container
./test.sh logs kafka         # Show Kafka logs

# Manual container inspection
docker ps | grep quix-test
docker exec quix-test-runner python --version
docker exec quix-test-runner pip list
```

---

## Testing Different App Types

### Source Applications (Produce to Kafka)

```python
def test_source_app(kafka_broker, test_topic):
    # 1. Setup topic
    create_topic(test_topic)

    # 2. Run source app
    run_app("/workspace/python/sources/my_source", {
        "output": test_topic,
        "Quix__Broker__Address": kafka_broker,
    })

    # 3. Consume and verify
    messages = consume_messages(test_topic, num=10)
    assert len(messages) == 10
    assert "expected_field" in messages[0]
```

### Destination Applications (Consume from Kafka)

```python
def test_destination_app(kafka_broker, test_topic):
    # 1. Produce test data
    produce_messages(test_topic, [
        {"id": 1, "value": "test1"},
        {"id": 2, "value": "test2"},
    ])

    # 2. Run destination app
    run_app("/workspace/python/destinations/postgres", {
        "input": test_topic,
        "Quix__Broker__Address": kafka_broker,
        "POSTGRES_HOST": "postgres",
        "POSTGRES_PORT": "5432",
        # ... other config
    })

    # 3. Verify data in destination
    import psycopg2
    conn = psycopg2.connect(
        host="postgres",
        port=5432,
        user="test_user",
        password="test_password",
        dbname="quix_test"
    )
    cursor = conn.execute("SELECT * FROM my_table")
    rows = cursor.fetchall()
    assert len(rows) == 2
```

### Transformation Applications (Consume + Transform + Produce)

```python
def test_transformation_app(kafka_broker):
    input_topic = f"test-input-{time.time()}"
    output_topic = f"test-output-{time.time()}"

    # 1. Setup topics
    create_topic(input_topic)
    create_topic(output_topic)

    # 2. Produce input
    produce_messages(input_topic, [{"value": 10}])

    # 3. Run transformation
    run_app("/workspace/python/transformations/my_transform", {
        "input": input_topic,
        "output": output_topic,
        "Quix__Broker__Address": kafka_broker,
    })

    # 4. Verify transformed output
    messages = consume_messages(output_topic, num=1)
    assert messages[0]["transformed_value"] == 20  # e.g., doubled
```

---

## Example: Full Test Suite

```python
"""
Complete example test for an application
"""
import pytest
import time
import subprocess
import json
from pathlib import Path
from confluent_kafka import Consumer, Producer
from confluent_kafka.admin import AdminClient, NewTopic


class TestMySource:
    @pytest.fixture(scope="class")
    def kafka_broker(self):
        return "kafka:9092"

    @pytest.fixture
    def test_topic(self):
        topic = f"test-{int(time.time())}"
        yield topic
        # Cleanup after test
        admin = AdminClient({"bootstrap.servers": "kafka:9092"})
        admin.delete_topics([topic])

    @pytest.fixture
    def app_dir(self):
        return Path("/workspace/python/sources/my_source")

    def run_app(self, app_dir, env_vars, timeout=10):
        env = os.environ.copy()
        env.update(env_vars)

        proc = subprocess.Popen(
            ["python", "main.py"],
            cwd=app_dir,
            env=env,
        )

        time.sleep(timeout)
        proc.terminate()
        proc.wait()

    def consume_all(self, topic, kafka_broker, timeout=10):
        consumer = Consumer({
            "bootstrap.servers": kafka_broker,
            "group.id": f"test-{time.time()}",
            "auto.offset.reset": "earliest",
        })
        consumer.subscribe([topic])

        messages = []
        start = time.time()

        while time.time() - start < timeout:
            msg = consumer.poll(1.0)
            if msg and not msg.error():
                messages.append(json.loads(msg.value()))
            elif not msg:
                break

        consumer.close()
        return messages

    def test_publishes_data(self, kafka_broker, test_topic, app_dir):
        """Test that source publishes data"""
        # Setup
        admin = AdminClient({"bootstrap.servers": kafka_broker})
        topic = NewTopic(test_topic, 1, 1)
        admin.create_topics([topic])

        # Run
        self.run_app(app_dir, {
            "output": test_topic,
            "Quix__Broker__Address": kafka_broker,
        }, timeout=5)

        # Verify
        messages = self.consume_all(test_topic, kafka_broker)
        assert len(messages) > 0, "Should publish messages"
        assert "expected_field" in messages[0]

    def test_data_structure(self, kafka_broker, test_topic, app_dir):
        """Test message structure is correct"""
        # ... similar pattern
        pass

    @pytest.mark.slow
    def test_continuous_publishing(self, kafka_broker, test_topic, app_dir):
        """Test that app publishes continuously"""
        # ... test with longer timeout
        pass
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test QuixStreams Samples

on: [pull_request, push]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v3

      - name: Start test infrastructure
        run: ./test.sh start-all

      - name: Run all tests
        run: ./test.sh test-all

      - name: Cleanup
        if: always()
        run: ./test.sh clean
```

---

## Troubleshooting

### Test container not building
```bash
# Rebuild from scratch
./test.sh build
```

### Can't connect to Kafka
```bash
# Check Kafka is running
docker ps | grep test-kafka

# Check network
docker network ls | grep quix-test

# Test from container
docker exec quix-test-runner bash -c "pip install kafka-python && python -c 'from kafka import KafkaProducer; p = KafkaProducer(bootstrap_servers=\"kafka:9092\"); print(\"Connected!\")'"
```

### Tests timing out
```bash
# Increase timeout in test
time.sleep(30)  # or subprocess timeout

# Check if app is actually running
docker exec quix-test-runner ps aux | grep python
```

### Need to add new Python dependency
```bash
# Edit test-infrastructure/requirements-test.txt
echo "my-new-package>=1.0.0" >> test-infrastructure/requirements-test.txt

# Rebuild
./test.sh build
```

### Interactive debugging
```bash
# Open shell in container
./test.sh test-shell

# Run tests with verbose output
pytest tests/sources/my_app/ -vv -s

# Or with debugger
pytest tests/sources/my_app/ --pdb
```

---

## Summary

**✅ Zero dependencies except Docker**
- No Make, no Python, nothing to install!

**✅ Pure bash + docker**
- Works everywhere bash works

**✅ Clean sample folders**
- Tests are separate from samples in `/tests/`
- Samples remain shippable and clean

**✅ Consistent test environment**
- Same container for all developers and CI/CD

**✅ Easy to add dependencies**
- Just edit requirements-test.txt and rebuild

**✅ Interactive development**
- Shell access for debugging

**✅ Simple commands**
- `./test.sh test-csv` - that's it!

**Goal: Validate that apps actually work, not just run!** 🚀