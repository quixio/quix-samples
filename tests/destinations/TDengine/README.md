# TDengine Destination Test

> **Note:** This is a comprehensive README that documents TDengine-specific concepts (supertables, subtables, tags vs fields) and database setup requirements. Most tests don't need this level of detail - only create extensive documentation when your test involves non-obvious technical concepts that would be difficult to understand from code alone.

## Introduction

TDengine is a time-series database optimized for IoT, IIoT, and other time-series data applications. This test validates the QuixStreams TDengine destination connector, which writes streaming data from Kafka to TDengine using the InfluxDB line protocol.

The test simulates a real-world IoT scenario with multiple sensors reporting temperature and humidity measurements over time.

## Test Architecture

This integration test follows a 4-step process:

1. **Setup TDengine Database** - Creates the `test_db` database using the setup script
2. **Produce Test Messages** - Writes sensor data messages to Kafka topic
3. **TDengine Destination Consumes** - The destination connector reads from Kafka and writes to TDengine
4. **Verify Data** - Queries TDengine to validate data was written correctly

The test is fully orchestrated using Docker Compose and runs end-to-end in a containerized environment.

## TDengine-Specific Setup

### Why Database Setup is Required

Unlike some databases that auto-create databases on first write, TDengine requires the database to exist before data can be written. The `setup_tdengine.py` script handles this initialization.

### What setup_tdengine.py Does

The setup script:
1. **Connects to TDengine** - Uses the REST API (port 6041) with default credentials
2. **Waits for TDengine** - Retries up to 10 times with 2-second delays to ensure TDengine is ready
3. **Creates Database** - Executes `CREATE DATABASE IF NOT EXISTS test_db`
4. **Skips Supertable Creation** - TDengine's InfluxDB API auto-creates supertables from the incoming line protocol data

### Connection Details

- Host: `tdengine` (container hostname)
- Port: `6041` (REST API port)
- Username: `root`
- Password: `taosdata` (default)
- Client Library: `taosrest` (Python REST connector)

## TDengine Data Model

TDengine uses a specialized data model optimized for time-series data from multiple devices:

### Supertable

**Name:** `sensor_data`

A supertable is a template that defines the schema for all sensor data. It is automatically created from the InfluxDB line protocol by the TDengine destination.

### Tags

**Tag:** `sensor_id` (string)

Tags identify the data source (device/sensor). In TDengine, tags are metadata that remain constant for a given device. Each unique tag combination automatically creates a subtable.

- `sensor_0` - First sensor (even-numbered messages)
- `sensor_1` - Second sensor (odd-numbered messages)

Tags enable efficient querying by device, e.g., "show me all data from sensor_0".

### Fields

**Field:** `temperature` (float)
**Field:** `humidity` (float)

Fields are the actual measured values that change over time. These are stored as time-series data points.

### Timestamp

**Column:** `timestamp` (millisecond precision)

Each record includes a timestamp in milliseconds since epoch. TDengine automatically indexes this column for efficient time-range queries.

### Why This Structure?

This data model is optimized for:
- **Efficient Storage** - Tags stored once per subtable, fields stored per measurement
- **Fast Queries** - Query by device (tags) or time range with high performance
- **Automatic Organization** - Subtables created automatically for each sensor_id
- **Scalability** - Handle millions of devices with billions of data points

## Running the Test

### Standard Test Framework

```bash
# From repository root
./test.py test destinations/TDengine
```

This is the recommended way to run the test as it uses the standard test framework.

### Direct Docker Compose

```bash
# Navigate to test directory
cd tests/destinations/TDengine

# Run the test
docker compose -f docker-compose.test.yml up --abort-on-container-exit

# Clean up
docker compose -f docker-compose.test.yml down -v
```

### Manual Verification

You can manually inspect the data written to TDengine:

```bash
# Connect to TDengine CLI
docker compose -f docker-compose.test.yml exec tdengine taos

# Query all data from supertable
SELECT * FROM test_db.sensor_data ORDER BY _ts;

# Query specific sensor
SELECT * FROM test_db.sensor_data WHERE sensor_id = 'sensor_0';

# Count records per sensor
SELECT sensor_id, COUNT(*) FROM test_db.sensor_data GROUP BY sensor_id;

# Show subtables (one per sensor)
SHOW test_db.TABLES LIKE 'sensor_%';
```

### Expected Output

The test produces 5 messages (configurable via `TEST_MESSAGE_COUNT`):
- Messages alternate between `sensor_0` and `sensor_1`
- Temperature values: 20.5, 21.0, 21.5, 22.0, 22.5
- Humidity values: 50.3, 52.5, 54.7, 56.9, 59.1
- Timestamps increment by 100ms per message

## Troubleshooting

### TDengine Client Installation Issues

**Symptom:** `ModuleNotFoundError: No module named 'taosrest'`

**Solution:** The test-runner installs `taospy` and `requests` automatically. If running manually:

```bash
pip install taospy requests
```

### Database Connection Errors

**Symptom:** Connection refused or timeout errors

**Solutions:**
1. Ensure TDengine container is healthy: `docker compose ps`
2. Check TDengine logs: `docker compose logs tdengine`
3. Verify healthcheck passes: TDengine executes `show databases;` successfully
4. Wait longer - TDengine can take 10-15 seconds to fully initialize

### Supertable Creation Failures

**Symptom:** Error querying `sensor_data` supertable

**Root Cause:** The destination connector may not have received/processed messages yet.

**Solutions:**
1. Verify Kafka has messages: Check `tdengine-dest` logs for consumption
2. Check destination logs for InfluxDB protocol errors
3. Ensure `TDENGINE_SUPERTABLE=sensor_data` environment variable is set
4. Verify `TDENGINE_NAME_SUBTABLES_FROM_TAGS=true` to enable automatic subtable creation

### Time-Series Data Validation Failures

**Symptom:** Data is written but validation fails

**Common Issues:**
1. **Wrong timestamp precision** - Ensure `TDENGINE_TIME_PRECISION=ms` matches test data (milliseconds)
2. **Missing fields** - Check that `TDENGINE_FIELDS_KEYS=temperature,humidity` matches message structure
3. **Tag mismatch** - Verify `TDENGINE_TAGS_KEYS=sensor_id` matches message key field
4. **Type conversion** - Enable `TDENGINE_CONVERT_INTS_TO_FLOATS=true` to ensure float storage

### UDF Crash Loop (udfd)

**Symptom:** TDengine container restarts repeatedly, logs show `udfd` process crashes

**Solution:** The test includes `taos.cfg` with `udf 0` to disable User-Defined Functions, which aren't needed for testing and can cause stability issues.

## Files in This Test

### test_tdengine_dest.py
Test metadata and documentation. Contains the pytest test class with detailed docstring explaining the integration test flow. The actual test logic is orchestrated in docker-compose.test.yml.

### setup_tdengine.py
Database initialization script that:
- Connects to TDengine via REST API
- Creates the `test_db` database
- Implements retry logic for container startup timing
- Does NOT create supertable (auto-created by InfluxDB API)

### produce_test_data.py
Kafka producer that generates test sensor data:
- Creates 5 messages (configurable)
- Alternates between `sensor_0` and `sensor_1`
- Generates realistic temperature/humidity float values
- Adds millisecond-precision timestamps
- Uses QuixStreams Application for production

### verify_output.py
TDengine data validator that:
- Queries the `sensor_data` supertable
- Verifies minimum row count (5 expected)
- Validates data structure (4 columns: timestamp, temperature, humidity, sensor_id)
- Checks for null values
- Confirms multiple sensor IDs present
- Implements retry logic for eventual consistency

### docker-compose.test.yml
Complete test orchestration with 4 services:
- **kafka** - Redpanda broker for message streaming
- **tdengine** - TDengine 3.3.0.0 database with custom config
- **tdengine-dest** - QuixStreams destination connector (built from source)
- **test-runner** - Executes setup, produce, wait, and verify steps

Includes healthchecks, networking, and proper dependency ordering.

### taos.cfg
TDengine server configuration:
- Disables UDF (`udf 0`) to prevent `udfd` crash loops
- Minimal configuration for stable testing

### produce_test_data.py (mentioned above)
Standard test data producer using QuixStreams framework.

## Configuration Reference

### TDengine Destination Environment Variables

Key configuration used in this test:

| Variable | Value | Purpose |
|----------|-------|---------|
| `TDENGINE_HOST` | `http://tdengine:6041` | REST API endpoint |
| `TDENGINE_DATABASE` | `test_db` | Target database |
| `TDENGINE_USERNAME` | `root` | Authentication username |
| `TDENGINE_PASSWORD` | `taosdata` | Authentication password |
| `TDENGINE_SUPERTABLE` | `sensor_data` | Supertable name |
| `TDENGINE_TAGS_KEYS` | `sensor_id` | Tag column(s) |
| `TDENGINE_FIELDS_KEYS` | `temperature,humidity` | Field column(s) |
| `TDENGINE_NAME_SUBTABLES_FROM_TAGS` | `true` | Auto-create subtables per tag |
| `TIMESTAMP_COLUMN` | `timestamp` | Timestamp field name |
| `TDENGINE_TIME_PRECISION` | `ms` | Millisecond precision |
| `TDENGINE_CONVERT_INTS_TO_FLOATS` | `true` | Ensure float type for numeric fields |

See the destination connector documentation for full configuration options.

## Migration Notes

This test was refactored from the pytest subprocess pattern to the standard docker-compose pattern in January 2025. The migration:

- Removed pytest subprocess orchestration in favor of docker-compose
- Converted standalone scripts to docker-compose services
- Maintained identical test logic and validation
- Improved test speed and reliability
- Added proper healthchecks and dependency management

See [MIGRATION_RESULTS.md](../../MIGRATION_RESULTS.md) for details on the standardization effort across all tests.

## References

### TDengine Documentation
- [TDengine Official Docs](https://docs.tdengine.com/)
- [TDengine Data Model](https://docs.tdengine.com/concept/)
- [TDengine InfluxDB Line Protocol](https://docs.tdengine.com/reference/connector/influxdb/)
- [TDengine Python Connector](https://docs.tdengine.com/reference/connector/python/)

### QuixStreams Documentation
- [QuixStreams TDengine Sink](https://quix.io/docs/quix-streams/connectors/sinks/tdengine.html)
- [QuixStreams Sinks Overview](https://quix.io/docs/quix-streams/connectors/sinks/overview.html)

### Test Framework
- [Main Test README](../../README.md) - Test framework overview and usage
- [MIGRATION_RESULTS.md](../../MIGRATION_RESULTS.md) - Test standardization documentation
