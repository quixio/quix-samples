# Variables Demo

[This code sample](https://github.com/quixio/quix-samples/tree/main/python/sources/variables-demo) demonstrates the Quix variable system end-to-end. A single library item declares three resolution mechanisms; on deployment the backend resolves each one into environment variables before the container starts, and the container logs the resolved values (the secret masked) plus emits one heartbeat to the output topic so resolution can be verified from the deployment logs.

## The three mechanisms

- **`InputType: ProjectVariable` (non-secret)** — `API_REGION` references a Project Variable. The `DefaultValue` (`demo_api_region`) is the *key* of the project variable to resolve, not a literal value. The backend resolves it to the variable's value before the container starts.
- **`InputType: ProjectVariable` with `"Secret": true`** — `API_SECRET` references a *secret* Project Variable (`demo_api_secret`). It is resolved from a Kubernetes secret and injected the same way as `API_REGION`, but is masked in the logs. The committed `library.json` never holds a real secret value — only the key to resolve.
- **`InputType: VariableGroup`** — `INFLUXDB_CONNECTION` references a shared Variable Group by its `VariableGroupId` (`influxdb-connection`). At deployment the selected value set is bulk-expanded into the individual environment variables declared under `Variables[]` (`INFLUXDB_HOST`, `INFLUXDB_PORT`, `INFLUXDB_ORG`) — all non-secret here.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Prerequisites in the workspace

Before deploying, create the references this sample resolves:

1. A **Project Variable** named `demo_api_region` with any non-empty value (non-secret).
2. A **secret Project Variable** named `demo_api_secret` with any non-empty value (mark it as secret so it is stored and delivered as a Kubernetes secret).
3. A **Variable Group** named `influxdb-connection` with at least one value set whose keys are `INFLUXDB_HOST`, `INFLUXDB_PORT`, and `INFLUXDB_ORG`. Make sure it is linked to the project (or environment) you are deploying into.

## Environment variables

The code sample uses the following environment variables:

- **output**: Output topic to write the heartbeat message into.
- **LOG_LEVEL**: Logging level for the container (optional, defaults to `INFO`).
- **API_REGION**: Reference to the non-secret Project Variable `demo_api_region`.
- **API_SECRET**: Reference to the secret Project Variable `demo_api_secret` (masked in logs).
- **INFLUXDB_HOST**, **INFLUXDB_PORT**, **INFLUXDB_ORG**: Injected from the `influxdb-connection` Variable Group.

## Verifying resolution

After deployment, open the container logs and look for the line:

```
Resolved variables from backend: {"API_REGION": "...", "API_SECRET": "ab***yz", "INFLUXDB_HOST": "...", "INFLUXDB_PORT": "...", "INFLUXDB_ORG": "..."}
```

`API_SECRET` is masked; every other value should show the resolved value. A `Missing required variables...` warning means a prerequisite above was not created or not linked. A `Published heartbeat to topic '<output>'` line confirms the single heartbeat reached the output topic.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
