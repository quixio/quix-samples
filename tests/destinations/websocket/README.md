# WebSocket Destination Test

Tests WebSocket destination forwarding Kafka messages to WebSocket clients with key-based routing and Basic Auth.

## Key-Based Routing

Kafka message key determines WebSocket path:
- Message with key `"channel1"` → sent to WebSocket path `/channel1`
- Clients connect to specific paths to receive only those messages

```python
# Producer sends with key
producer.produce(topic="input", key="channel1", value=data)

# Client connects to matching path
ws://host:port/channel1
```

## Why Async Test Pattern

WebSocket client must connect BEFORE messages are produced. Messages sent when no clients are connected are discarded.

The test uses `verify_and_produce.py` which:
1. Connects WebSocket client to `/channel1`
2. Produces messages with key `"channel1"` to Kafka (concurrent)
3. Validates messages received via WebSocket

## Running the Test

```bash
./test.py test destinations/websocket
```

## Troubleshooting

**No messages received**: Client must connect before producer sends. The test handles this via concurrent execution.

**Authentication failures**: Check `WS_USERNAME` and `WS_PASSWORD` match in destination and test-runner.

**Timeouts**: Increase sleep or timeout values in docker-compose.test.yml if needed:
- Line 52: `sleep 8` (startup delay)
- Line 24 in verify_output.py: `asyncio.timeout(25)`
- Line 27 in verify_and_produce.py: `asyncio.timeout(20)`

## Files

- `verify_and_produce.py` - Main test script (connects client + produces messages concurrently)
- `produce_test_data.py` - Standalone producer (not used by main test)
- `verify_output.py` - Standalone verifier (not used by main test)
- `docker-compose.test.yml` - Orchestrates test using `verify_and_produce.py`
