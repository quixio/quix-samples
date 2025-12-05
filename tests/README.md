# QuixStreams Samples - Integration Tests

Docker Compose integration tests for QuixStreams sample applications.

---

## Quick Start

```bash
# Run specific test
./test.py test sources/starter_source

# Run all tests
./test.py test-all

# Run all tests in parallel (with auto-retry)
./test.py test-all --parallel 3
./test.py test-all -p 3

# Run by category
./test.py test-sources
./test.py test-destinations -p 4
./test.py test-transformations --parallel 2

# Run multiple specific tests
./test.py test sources/starter_source destinations/influxdb_3 -p 2

# Set timeout (default: 300s / 5min)
./test.py test sources/slow_source --timeout 600
./test.py test-all -p 3 -t 180

# List available tests
./test.py list

# Find apps that need tests
./test.py list-untested
```

---

## Timeouts

Each test has a maximum runtime limit to prevent stuck tests:

**Default:** 300 seconds (5 minutes)

**Per-test override:** Add a comment to the top of `docker-compose.test.yml`:
```yaml
# timeout: 600
services:
  your-service:
    ...
```

**Global override:** Use the `-t` / `--timeout` flag:
```bash
./test.py test-all -p 3 --timeout 180  # 3 minutes
```

Priority: per-test override > CLI flag > default (300s)

---

## Test Architecture

The test suite uses a **script-based validation pattern**. Docker Compose orchestrates the flow:

```
docker-compose.test.yml orchestrates:
  1. Kafka (Redpanda) starts (for integration tests)
  2. Application under test starts
  3. Test-runner executes validation scripts:
     - produce_test_data.py (for destinations/transformations)
     - Wait for processing
     - verify_output.py validates results

Build-only tests skip Kafka and use entrypoint override for syntax validation.
```

---

## Test Types

| Type | Kafka Required | Scripts Needed | Purpose |
|------|---------------|----------------|---------|
| **Full Integration** | Yes | `verify_output.py` + optional `produce_test_data.py` | Validates end-to-end functionality with real Kafka |
| **Build-Only** | No | None | Validates Docker build and syntax for apps with complex external dependencies |

**Full Integration:**
- **Sources**: App → Kafka output topic → verify
- **Destinations**: Kafka input topic → app → external service → verify
- **Transformations**: Kafka input → app → Kafka output → verify

**Build-Only:** Used when full testing is impractical (external auth, large downloads, proprietary services).

---

## File Structure

### Source Test
```
tests/sources/[app_name]/
├── docker-compose.test.yml
└── verify_output.py
```

### Destination/Transformation Test
```
tests/[category]/[app_name]/
├── docker-compose.test.yml
├── produce_test_data.py
└── verify_output.py
```

### Build-Only Test
```
tests/[category]/[app_name]/
└── docker-compose.test.yml  # Uses entrypoint override for syntax check
```

---

## Reference Implementations

Copy these as starting points:

- **Source**: `tests/sources/starter_source/`
- **Destination**: `tests/destinations/influxdb_3/`
- **Transformation**: `tests/transformations/event_detection/`
- **Build-Only**: `tests/transformations/hugging_face_model/`

---

## Adding New Tests

### Source Test
```bash
cp -r tests/templates/source tests/sources/your_app
cd tests/sources/your_app
```

Follow the TODO comments in each file. See `README.md` in the template for checklist.

**Run:**
```bash
./test.py test sources/your_app
```

### Destination Test
```bash
cp -r tests/templates/destination tests/destinations/your_dest
cd tests/destinations/your_dest
```

Follow the TODO comments in each file. See `README.md` in the template for checklist.

**Run:**
```bash
./test.py test destinations/your_dest
```

### Transformation Test
```bash
cp -r tests/templates/transformation tests/transformations/your_transform
cd tests/transformations/your_transform
```

Follow the TODO comments in each file. See `README.md` in the template for checklist.

**Run:**
```bash
./test.py test transformations/your_transform
```

### Build-Only Test
```bash
cp -r tests/templates/build-only tests/[category]/your_app
cd tests/[category]/your_app
```

Follow the TODO comments. Explain why build-only in test docstring.

**Run:**
```bash
./test.py test [category]/your_app
```

---

## Troubleshooting

### Common Commands

| Issue | Command |
|-------|---------|
| Check Kafka health | `docker compose -f tests/.../docker-compose.test.yml logs kafka` |
| Check app logs | `docker compose -f tests/.../docker-compose.test.yml logs [app-name]` |
| List topics | `docker compose -f tests/.../docker-compose.test.yml exec kafka rpk topic list` |
| Consume topic | `docker compose -f tests/.../docker-compose.test.yml exec kafka rpk topic consume [topic] --num 5` |
| Run verify manually | `docker compose -f tests/.../docker-compose.test.yml run test-runner python /tests/verify_output.py` |
| Interactive debug | `docker compose -f tests/.../docker-compose.test.yml run test-runner sh` |
| Force cleanup | `docker ps -q \| xargs docker stop; docker system prune -f` |

### Common Issues

| Issue | Solution |
|-------|----------|
| Port conflicts | `docker ps` then `docker stop [container]` |
| Stale containers | `docker ps -q \| xargs docker stop` |
| Build cache | Add `--build` or `docker compose build --no-cache` |
| Permission errors | `chmod +r verify_output.py produce_test_data.py` |
| Network not found | Check `networks` section in docker-compose.test.yml |

---

## Requirements

- **Python 3.7+** (test runner uses only standard library; validation scripts may use quixstreams)
- **Docker**
- **Docker Compose v2**

Check versions:
```bash
python3 --version
docker --version
docker compose version
```

---

## More Information

```bash
./test.py help
```

For migration history:
- `PYTHON_MIGRATION_PLAN.md` - Python migration plan and results
