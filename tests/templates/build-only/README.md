# Build-Only Test Template

⚠️ **DELETE THIS FILE after copying the template** (unless your test has special complexity that needs explanation)

This template is for apps that can't run full integration tests due to external dependencies.

## Quick Copy
```bash
cp -r tests/templates/build-only tests/[category]/your_app
cd tests/[category]/your_app
# After completing the checklist below, delete this README:
rm README.md
```

## When to Use Build-Only

Use this template when full integration testing is impractical:
- External services require authentication (APIs, SaaS platforms)
- Large downloads (ML models, datasets)
- Proprietary services not available in Docker
- Resource-intensive operations

## What Build-Only Tests Do

Build-only tests validate Docker build and Python syntax without running the full application:
- Build the Docker image to catch build errors
- Use `entrypoint` override to run Python syntax check (`python -m py_compile main.py`)
- No Kafka or external services needed

## What to Customize

**docker-compose.test.yml:**
- [ ] Service name: `[app-name]`
- [ ] Build context path: Point to your app directory (e.g., `../../../python/transformations/your_app`)
- [ ] Entrypoint: Update `main.py` to your app's entry point if different
- [ ] Optional: Add comment with timeout if needed

## Example Structure

```yaml
# timeout: 120
services:
  your-app:
    build:
      context: ../../../python/transformations/your_app
      dockerfile: Dockerfile
    entrypoint: ["python", "-m", "py_compile", "main.py"]
```

## Run Test
```bash
./test.py test [category]/your_app
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
See main test README: `../../../tests/README.md`
