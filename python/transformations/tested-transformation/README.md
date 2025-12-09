# Tested Transformation Template

This template demonstrates how to build and test a Quix Streams transformation application with proper separation of concerns and comprehensive testing.

## Project Structure

```
tested-transformation/
├── main.py           # Production code with pipeline definition
├── test.py           # Test suite with mocked data source
├── utils.py          # Shared testing utilities
└── README.md         # This file
```

## Testing Strategy

This template showcases best practices for testing Quix Streams applications:

### 1. Separation of Pipeline Logic

The pipeline transformation logic is isolated in the `define_pipeline()` function in `main.py`. This function:
- Takes a `StreamingDataFrame` as input
- Applies all transformations
- Returns the transformed `StreamingDataFrame`

This separation allows the same pipeline logic to be used in both production (with Kafka topics) and testing (with mocked data sources).

### 2. Mocked Data Source

`test.py` includes a `TestDataSource` class that:
- Extends `quixstreams.sources.Source`
- Produces deterministic test data with known timestamps
- Includes dummy messages at the end to close windowed aggregations
- Eliminates the need to publish test data to Kafka topics manually

**Note:** While the data source is mocked, these are still **integration tests** - Quix Streams internally uses Kafka for state management and processing. A Kafka broker is required to run the tests.

### 3. Deterministic Assertions

The test suite uses a structured approach:
- **Expected output is defined upfront** as a list of dictionaries with expected values
- **Messages are grouped by key** to handle partition-based ordering (messages from different keys may arrive in any order)
- **Order is verified within each key** to ensure temporal correctness per partition
- **Utility function handles comparison** via `assert_messages_match()` in `utils.py`

### 4. Key Testing Considerations

**Windowing:** When testing windowed operations, remember:
- Windows only emit results when they close
- Add dummy messages with future timestamps to close the final window
- Window boundaries align to fixed time intervals from epoch, not event arrival times

**Partitioning:** In Kafka/Quix Streams:
- Messages with different keys may be processed in different partitions
- Order is guaranteed only within a single key/partition
- Tests must group by key before asserting order

**Unique Consumer Groups:** Use `uuid.uuid4()` for consumer groups and source names in tests to ensure each test run is isolated.

**Kafka Requirement:** Quix Streams uses Kafka internally for state management (RocksDB state stores are backed by changelog topics). The provided `compose.test.yaml` file starts a local Kafka broker and Redpanda Console for debugging:
- Kafka broker: `localhost:19092`
- Redpanda Console: `http://localhost:8080` (optional web UI for inspecting topics)

## Running Tests

### Prerequisites

Tests require a running Kafka broker. Use the provided Docker Compose file to start Kafka locally:

```bash
# Start Kafka in the background
docker-compose -f compose.test.yaml up -d

# Wait a few seconds for Kafka to be ready
```

### Run the Tests

```bash
# Run the test suite
python test.py
```

### Cleanup

```bash
# Stop Kafka when done
docker-compose -f compose.test.yaml down -v
```

Expected output:
```
✓ Received 7 messages

--- Verifying messages for key: host1 ---
Message 1 for key 'host1':
  Expected: start=1577836800000, end=1577836803000, value=1
  Actual:   start=1577836800000, end=1577836803000, value=1
  ✓ Match!
...
✓ All assertions passed!
✓ All 7 messages matched expected output across 2 keys
```

## Running in Production

```bash
# Run the production application
python main.py
```

The production application requires environment variables:
- `input`: Name of the input Kafka topic
- `output`: Name of the output Kafka topic

## How to Use This Template

1. **Modify the pipeline**: Update `define_pipeline()` in `main.py` with your transformation logic
2. **Update test data**: Modify `TestDataSource.memory_allocation_data` to match your input schema
3. **Update expected output**: Change `expected_rows` in `test.py` to match your pipeline's expected results
4. **Run tests**: Execute `python test.py` to verify your pipeline works correctly
5. **Deploy**: Deploy `main.py` to production

## Example: Understanding the Test

The template includes a tumbling window aggregation that counts events per 3-second window:

```python
sdf = sdf.tumbling_window(3000).count().final()
```

**Input events** (7 events across 2 hosts):
- host1: timestamps 800, 803, 806, 810 (ms)
- host2: timestamps 801, 804, 808 (ms)

**Window boundaries** (3000ms windows from epoch):
- [800, 803): host1=1, host2=1
- [803, 806): host1=1, host2=1
- [806, 809): host1=1, host2=1
- [809, 812): host1=1

**Output**: 7 windowed count results (one per host per window)

## Best Practices

1. **Keep pipeline logic pure**: The `define_pipeline()` function should only transform data, not handle I/O
2. **Use realistic test data**: Mirror production data structures and edge cases
3. **Test temporal operations**: Pay special attention to windowing, time-based joins, and stateful operations
4. **Isolate test runs**: Use unique consumer groups to prevent state pollution between test runs
5. **Document window mechanics**: Clearly explain how windowing aligns and when windows close

## Learn More

- [Quix Streams Documentation](https://quix.io/docs/quix-streams/introduction.html)
- [StreamingDataFrame Operations](https://quix.io/docs/quix-streams/processing.html)
- [Windowing Guide](https://quix.io/docs/quix-streams/windowing.html)
- [Testing Stateful Applications](https://quix.io/docs/quix-streams/testing.html)