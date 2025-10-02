# WebSocket Destination Test

> **Note:** This is a comprehensive README that documents complex async patterns and key-based routing. Most tests don't need this level of detail - only create extensive documentation when your test involves non-obvious technical concepts that would be difficult to understand from code alone.

This test validates that the WebSocket destination correctly forwards Kafka messages to WebSocket clients with key-based routing and authentication.

## What This Test Validates

The WebSocket destination test verifies:
- WebSocket destination consumes messages from Kafka and forwards them to connected clients
- Key-based routing correctly maps Kafka message keys to WebSocket paths
- Basic Authentication is properly enforced for WebSocket connections
- Message structure and content are preserved during forwarding

## Test Architecture

### Flow Overview

```
┌─────────────┐     ┌─────────┐     ┌──────────────────────┐     ┌──────────────┐
│  Producer   │────>│  Kafka  │────>│ WebSocket Destination│────>│ WS Client    │
│             │     │         │     │ (consumes & serves)  │     │ (verifier)   │
└─────────────┘     └─────────┘     └──────────────────────┘     └──────────────┘
```

### Sequential Execution

Unlike parallel producer/consumer tests, this test uses a concurrent approach to ensure proper message delivery:

1. **WebSocket Destination Starts**: Begins consuming from Kafka and serving WebSocket connections
2. **Verifier Connects**: WebSocket client connects to `/channel1` with authentication and stays connected
3. **Producer Sends Messages**: Produces messages with key `"channel1"` to Kafka topic while client is listening
4. **Destination Routes Messages**: Reads from Kafka and broadcasts to connected WebSocket clients at path `/channel1`
5. **Verifier Receives**: Client receives messages in real-time and validates structure

This execution flow is critical because:
- **WebSocket client must connect BEFORE messages are produced**: The destination only forwards messages to currently connected clients. Messages consumed when no clients are connected are discarded.
- The WebSocket server must be ready before the client connects
- The producer and receiver must run concurrently to handle the real-time streaming nature of WebSockets

## Key-Based Routing

### How It Works

The WebSocket destination implements a pub/sub pattern where:
- **Kafka message key** determines the **WebSocket path**
- Message with key `"channel1"` → sent to WebSocket path `/channel1`
- Clients connect to specific paths to receive only those messages
- Multiple channels can coexist on one WebSocket server

### Example

```python
# Producer sends with key
producer.produce(
    topic="test-websocket-input",
    key="channel1",        # This becomes the path
    value=message_data
)

# Client connects to matching path
url = f"ws://{host}:{port}/channel1"  # Must match the key
```

This enables:
- **Multiple rooms/channels** in a single WebSocket server
- **Selective message delivery** - clients only receive relevant messages
- **Scalable pub/sub** - new channels created dynamically from message keys

## Async WebSocket Pattern

### Why Async Is Required

WebSocket communication is inherently asynchronous:
- Connections remain open for bidirectional communication
- Messages arrive at unpredictable times
- Multiple concurrent connections need non-blocking I/O

### Implementation

The verifier uses Python's `asyncio` and `websockets` library:

```python
async def websocket_client(received_messages, ...):
    async with websockets.connect(url, additional_headers=headers) as websocket:
        async with asyncio.timeout(15):  # 15-second collection window
            while True:
                message = await websocket.recv()  # Non-blocking receive
                received_messages.append(json.loads(message))

# Run the async coroutine
asyncio.run(main())
```

**Key aspects:**
- `async/await` syntax for non-blocking operations
- `asyncio.timeout(15)` provides collection window (not a hard timeout)
- `websocket.recv()` waits asynchronously for messages
- Graceful handling of `TimeoutError` and `ConnectionClosed`

## Authentication

### Basic Auth Implementation

The WebSocket destination enforces HTTP Basic Authentication:

```python
# Client creates auth header
credentials = f"{username}:{password}"
encoded = base64.b64encode(credentials.encode()).decode()
headers = {"Authorization": f"Basic {encoded}"}

# Include in WebSocket connection
async with websockets.connect(url, additional_headers=headers) as ws:
    # Connection only succeeds with valid credentials
```

**Environment Variables:**
- `WS_USERNAME=testuser` - Username for authentication
- `WS_PASSWORD=testpass` - Password for authentication

**Security Notes:**
- Credentials sent in WebSocket handshake
- Server validates before allowing connection
- In production, use WSS (WebSocket Secure) with TLS
- Basic Auth transmitted in clear text over WS (encrypted over WSS)

## Running the Test

### Standard Method

Using the test framework:

```bash
./test.py test destinations/websocket
```

### Direct Docker Compose

```bash
cd tests/destinations/websocket
docker compose -f docker-compose.test.yml up --abort-on-container-exit
```

### Manual Step-by-Step Testing

For debugging or exploration:

```bash
cd tests/destinations/websocket

# 1. Start Kafka and WebSocket destination
docker compose -f docker-compose.test.yml up -d kafka websocket-destination

# 2. Wait for services to be ready (check logs)
docker compose -f docker-compose.test.yml logs -f websocket-destination

# 3. Produce test messages (in another terminal)
docker compose -f docker-compose.test.yml run --rm test-runner \
    python /tests/produce_test_data.py

# 4. Verify WebSocket output (in another terminal)
docker compose -f docker-compose.test.yml run --rm test-runner \
    sh -c "pip install websockets && python /tests/verify_output.py"

# 5. Cleanup
docker compose -f docker-compose.test.yml down -v
```

## Troubleshooting

### WebSocket Connection Refused

**Symptoms:**
- `Connection refused` or `Cannot connect to WebSocket`

**Causes & Solutions:**
- **Server not ready**: Wait longer after starting destination (increase sleep time)
- **Wrong host/port**: Verify `WS_HOST=websocket-destination` and `WS_PORT=80`
- **Network issues**: Check Docker network configuration

**Debug:**
```bash
docker compose logs websocket-destination
docker compose exec test-runner nc -zv websocket-destination 80
```

### Authentication Failures

**Symptoms:**
- `401 Unauthorized` or connection rejected immediately

**Causes & Solutions:**
- **Wrong credentials**: Verify `WS_USERNAME` and `WS_PASSWORD` match in both services
- **Missing auth header**: Check Base64 encoding of credentials
- **Server config**: Ensure destination has auth enabled

**Debug:**
```bash
# Check environment variables
docker compose config | grep -A5 websocket-destination
```

### Timeout Without Receiving Messages

**Symptoms:**
- WebSocket connects but times out with 0 messages received

**Causes & Solutions:**
- **Client connects too late**: The WebSocket destination only forwards messages to currently connected clients. If messages are consumed from Kafka before any clients are connected, those messages are lost.
  - **Solution**: Ensure WebSocket client connects BEFORE messages are produced
  - The test uses a concurrent approach: client connects first, then producer sends messages while client is listening
- **Key routing mismatch**: Producer key must match WebSocket path
  - Producer uses `key="channel1"`
  - Client connects to `/channel1`
- **Kafka topic issues**: Verify topic exists and messages are produced

**Debug:**
```bash
# Check Kafka topic
docker compose exec kafka rpk topic consume test-websocket-input --num 5

# Check producer output
docker compose logs test-runner | grep "Producing message"

# Check destination logs
docker compose logs websocket-destination | grep -i channel

# Check connection timing
docker compose logs test-runner | grep -E "(WebSocket|Producer)"
```

### Message Count Mismatch

**Symptoms:**
- Received fewer messages than expected

**Causes & Solutions:**
- **Race condition**: Messages sent before client connected (add delay)
- **Timeout too short**: Increase from 15s if network is slow
- **Destination lag**: Add sleep between producer and verifier
- **Connection dropped**: Check for `ConnectionClosed` in logs

**Debug:**
```bash
# Increase timeouts in docker-compose.test.yml
# Line 54: sleep 5 -> sleep 10  (before verifier)
# Line 25 in verify_output.py: timeout(15) -> timeout(30)
```

## Files in This Test

### `verify_and_produce.py`
- **Main test script** that orchestrates the test execution
- Runs WebSocket client and producer concurrently using asyncio
- Ensures client connects BEFORE messages are produced (critical for test success)
- Validates message count and structure
- Combines both producer and consumer logic in one coordinated flow

### `produce_test_data.py`
- Standalone producer script for producing test messages to Kafka
- Uses QuixStreams Application for producing
- Sends messages with key `"channel1"` for routing
- Creates 5 messages (configurable via `TEST_MESSAGE_COUNT`)
- **Note**: For the test to work, this must run AFTER WebSocket client connects

### `verify_output.py`
- Standalone async WebSocket client that validates output
- Connects to WebSocket with Basic Auth
- Receives messages for 25 seconds
- Validates message count and structure
- **Note**: Can be used independently but timing with producer is critical

### `docker-compose.test.yml`
- Orchestrates Kafka, WebSocket destination, and test runner
- Configures environment variables for all services
- Runs concurrent test: client connects → producer sends → verify
- Includes health checks and dependencies

## Migration Notes

This test was migrated from a combined `test_websocket.py` to separate producer/verifier scripts for:

**Better Clarity:**
- Separate concerns: producing vs verifying
- Easier to understand data flow
- Simpler debugging (run scripts independently)

**Improved Maintainability:**
- Producer logic in `produce_test_data.py`
- Verifier logic in `verify_output.py`
- Clear separation between test setup and validation

**Enhanced Reusability:**
- Scripts can be run independently for manual testing
- Easier to adapt for different scenarios
- Better documentation through code organization

## Environment Variables

### Producer (`produce_test_data.py`)
- `Quix__Broker__Address` - Kafka broker address (default: `kafka:9092`)
- `TEST_INPUT_TOPIC` - Topic to produce to (default: `test-websocket-input`)
- `TEST_MESSAGE_COUNT` - Number of messages to send (default: `5`)

### Verifier (`verify_output.py`)
- `WS_HOST` - WebSocket server host (default: `websocket-destination`)
- `WS_PORT` - WebSocket server port (default: `80`)
- `WS_USERNAME` - Auth username (default: `testuser`)
- `WS_PASSWORD` - Auth password (default: `testpass`)
- `TEST_MESSAGE_COUNT` - Expected message count (default: `5`)

### WebSocket Destination
- `Quix__Broker__Address` - Kafka broker to consume from
- `input` - Input topic name
- `WS_USERNAME` - Required username for client auth
- `WS_PASSWORD` - Required password for client auth

## References

### Documentation
- [WebSocket Protocol (RFC 6455)](https://datatracker.ietf.org/doc/html/rfc6455)
- [Python websockets library](https://websockets.readthedocs.io/)
- [Python asyncio](https://docs.python.org/3/library/asyncio.html)
- [HTTP Basic Authentication](https://datatracker.ietf.org/doc/html/rfc7617)

### Related Tests
- [Main test framework README](../../README.md)
- [Test standardization plan](../../TEST_STANDARDIZATION_PLAN.md)

### QuixStreams
- [QuixStreams documentation](https://quix.io/docs/quix-streams/introduction.html)
- [WebSocket destination source code](../../../python/destinations/websocket)
