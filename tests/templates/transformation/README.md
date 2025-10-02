# Transformation Test Template

⚠️ **DELETE THIS FILE after copying the template** (unless your test has special complexity that needs explanation)

Copy this template to create a new transformation test.

## Quick Copy
```bash
cp -r tests/templates/transformation tests/transformations/your_app
cd tests/transformations/your_app
# After completing the checklist below, delete this README:
rm README.md
```

## Test Flow

Transformation tests validate that your app reads from Kafka, transforms data, and writes back to Kafka:

```
1. Kafka (Redpanda) starts
2. Your transformation app starts
3. produce_test_data.py sends messages to input topic
4. App processes and transforms messages
5. App writes transformed messages to output topic
6. verify_output.py consumes from output topic and validates results
```

## Files Structure

```
tests/transformations/your_app/
├── docker-compose.test.yml  # Orchestrates Kafka, app, and test-runner
├── produce_test_data.py      # Sends test messages to input topic
└── verify_output.py          # Validates transformed output messages
```

## What to Customize

**docker-compose.test.yml:**
- [ ] Service name: `your-app`
- [ ] Build context path: `../../transformations/your_app`
- [ ] Environment variables (especially `input` and `output`)
- [ ] Topic names (must match produce_test_data.py and verify_output.py)
- [ ] Add external services if needed (cache, ML model, API)
- [ ] Optional: Add timeout comment if > 5 minutes needed

**produce_test_data.py:**
- [ ] Input topic name (must match docker-compose.test.yml)
- [ ] Input message structure (fields and values)
- [ ] Message count (typically 5-10 for testing)
- [ ] Test data that exercises your transformation logic
- [ ] Add dummy message for windowing if needed

**verify_output.py:**
- [ ] Output topic name (must match docker-compose.test.yml)
- [ ] Output message structure validation
- [ ] Transformed field validations (check transformation logic worked)
- [ ] Expected count (use `TEST_MIN_EXPECTED_COUNT` for filtering/aggregation)
- [ ] Timeout duration if different from 60 seconds

## Run Test
```bash
./test.py test transformations/your_app
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
