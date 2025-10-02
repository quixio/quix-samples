# Source Test Template

⚠️ **DELETE THIS FILE after copying the template** (unless your test has special complexity that needs explanation)

Copy this template to create a new source test.

## Quick Copy
```bash
cp -r tests/templates/source tests/sources/your_app
cd tests/sources/your_app
# After completing the checklist below, delete this README:
rm README.md
```

## Test Flow

Source tests validate that your app produces messages to Kafka:

```
1. Kafka (Redpanda) starts
2. Your source app starts → produces messages to output topic
3. verify_output.py consumes from output topic and validates messages
```

## Files Structure

```
tests/sources/your_app/
├── docker-compose.test.yml  # Orchestrates Kafka, app, and test-runner
└── verify_output.py          # Validates output messages
```

## What to Customize

**docker-compose.test.yml:**
- [ ] Service name: `your-app`
- [ ] Build context path: `../../sources/your_app`
- [ ] Environment variables (especially `output`)
- [ ] Topic name (must match verify_output.py)
- [ ] Add external services if needed (database, API mock, etc.)
- [ ] Optional: Add timeout comment if > 5 minutes needed

**verify_output.py:**
- [ ] Topic name (must match docker-compose.test.yml)
- [ ] Expected message count: `TEST_MIN_EXPECTED_COUNT`
- [ ] Field validations (check for required fields, types, value ranges)
- [ ] Timeout duration if different from 60 seconds

## Run Test
```bash
./test.py test sources/your_app
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
