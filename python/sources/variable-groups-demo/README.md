# Variable Groups Demo

Reference library item demonstrating the redesigned variable system end-to-end:

- **`InputType: ProjectVariable`** — `API_KEY` references a Project Variable named `demo_api_key`. The backend resolves the reference to the variable's value before the container starts.
- **`InputType: Group`** — `INFLUXDB_CONNECTION` declares a Variable Group schema (`INFLUXDB_HOST`, `INFLUXDB_PORT`, `INFLUXDB_TOKEN`). At deployment time the user picks a Variable Group whose schema matches; the selected value set is injected as individual environment variables, with `Secret: true` keys delivered as Kubernetes secrets.

The container logs the resolved values (secrets masked) and produces a single heartbeat message to the configured output topic, so successful resolution can be verified from the deployment logs and the topic.

## Prerequisites in the workspace

Before deploying:

1. Create a Project Variable `demo_api_key` with any non-empty value.
2. Create a Variable Group `influxdb-demo` with at least one value set whose keys are `INFLUXDB_HOST`, `INFLUXDB_PORT`, `INFLUXDB_TOKEN`. Make sure it is linked to the Project (or Environment) you are deploying into.

## Files

- `library.json` — manifest read by the Quix portal-library service.
- `main.py` — Quix Streams source that logs resolved variables and emits a heartbeat.
- `dockerfile`, `requirements.txt` — container build inputs.
