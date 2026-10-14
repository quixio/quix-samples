# Destination Test Template

⚠️ **DELETE THIS FILE after copying the template** (unless your test has special complexity that needs explanation)

Copy this template to create a new destination test.

## Quick Copy
```bash
cp -r tests/templates/destination tests/destinations/your_app
cd tests/destinations/your_app
# After completing the checklist below, delete this README:
rm README.md
```

## Test Flow

Destination tests validate that your app consumes from Kafka and writes to an external system:

```
1. Kafka (Redpanda) starts
2. Destination service starts (database, API, etc.)
3. Your destination app starts
4. produce_test_data.py sends messages to input topic
5. App processes messages and writes to destination
6. verify_output.py queries destination and validates data
```

## Files Structure

```
tests/destinations/your_app/
├── docker-compose.test.yml  # Orchestrates Kafka, destination service, app, test-runner
├── produce_test_data.py      # Sends test messages to Kafka
└── verify_output.py          # Queries destination and validates results
```

## What to Customize

**docker-compose.test.yml:**
- [ ] Add destination service (database, API mock, etc.)
- [ ] Service name: `your-app`
- [ ] Build context path: `../../../python/destinations/your_app`
- [ ] Environment variables (especially `input`)
- [ ] Topic name (must match produce_test_data.py)
- [ ] Install client library in test-runner `command` section (e.g., `pip install psycopg2-binary`)
- [ ] Optional: Add timeout comment if > 5 minutes needed

**produce_test_data.py:**
- [ ] Topic name (must match docker-compose.test.yml)
- [ ] Message structure (fields and values)
- [ ] Message count (typically 5-10 for testing)

**verify_output.py:**
- [ ] Import destination client library
- [ ] Connection parameters (host, port, credentials)
- [ ] Query logic to retrieve data from destination
- [ ] Field validations (check all expected fields are present and correct)
- [ ] Expected record count

## Run Test
```bash
./test.py test destinations/your_app
```

## If Your Test Has Special Complexity

Most tests should DELETE this README after copying. However, if your test has unique requirements or complexity, KEEP and UPDATE this README to explain:

- Special setup requirements (e.g., database initialization)
- Non-obvious configuration
- Manual verification steps
- Troubleshooting common issues

**Examples of tests with useful READMEs:**
- `tests/destinations/TDengine/` - Complex database setup, data model explanation
- `tests/destinations/websocket/` - Async patterns, key-based routing

## More Help
See main test README: `../../../README.md`
