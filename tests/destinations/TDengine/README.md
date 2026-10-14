# TDengine Destination Test

Tests the TDengine destination connector writing sensor data to TDengine database.

## Why This Test Needs Setup

TDengine requires the database to exist before writing data. The `setup_tdengine.py` script creates the `test_db` database.

## TDengine Data Model

- **Supertable**: `sensor_data` (auto-created by destination)
- **Tags**: `sensor_id` (identifies device)
- **Fields**: `temperature`, `humidity` (measured values)
- **Subtables**: Auto-created per unique `sensor_id`

This structure enables efficient querying by device and time range.

## Running the Test

```bash
./test.py test destinations/TDengine
```

## Manual Verification

```bash
# Connect to TDengine CLI
docker compose -f docker-compose.test.yml exec tdengine taos

# Query data
SELECT * FROM test_db.sensor_data ORDER BY _ts;
SELECT sensor_id, COUNT(*) FROM test_db.sensor_data GROUP BY sensor_id;
```

## Troubleshooting

**Database connection errors**: Wait 10-15 seconds for TDengine to fully initialize.

**UDF crash loop**: Custom `taos.cfg` disables UDF to prevent `udfd` crashes during testing.

**Authentication**: Test uses username/password auth (not token) for on-premise TDengine compatibility.

## Files

- `setup_tdengine.py` - Creates database via REST API
- `produce_test_data.py` - Sends sensor data to Kafka
- `verify_output.py` - Queries TDengine and validates data
- `taos.cfg` - Disables UDF to prevent crashes
- `docker-compose.test.yml` - Orchestrates test (1 message by default, configurable via `TEST_MESSAGE_COUNT`)
