# QuixLab

This sample deploys [QuixLab](https://github.com/quixio/quixlab) — a reactive
canvas notebook for realtime data — onto the Quix platform. QuixLab combines
the spatial freedom of an infinite canvas with reactive Python cells, and
wires directly into the Quix data plane: SQL queries against the QuixLake,
live Kafka topics via `quixstreams`, and blob storage as first-class variables.

## How to Run

1. Log in or sign up at [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch the QuixLab service.
3. Configure the environment variables (or accept the defaults).
4. Open the deployment — QuixLab is embedded directly in the Quix UI via the sidebar item.
5. Use the file picker inside QuixLab to create your first notebook. Notebooks are stored on the persistent state volume and survive restarts.

## Environment Variables

| Variable           | Description                                                                  | Default |
| ------------------ | ---------------------------------------------------------------------------- | ------- |
| `QUIXLAB_NOTEBOOK` | Notebook file to open on startup. Leave empty to land on the file picker.   | (empty) |
| `QUIXLAB_MODE`     | `edit` (full editor) or `app` (read-only output view).                       | `edit`  |

The Quix-managed token (`Quix__Sdk__Token`) and workspace
(`Quix__Workspace__Id`) are injected automatically by the platform, so
`ql.sql(...)` and `ql.topic(...)` work out of the box.

## What you can do in a notebook

```python
import quixlab as ql

canvas = ql.Canvas(title="My Dashboard")

# SQL against the QuixLake
@canvas.dataset()
def laps():
    return ql.sql("SELECT * FROM telemetry LIMIT 1000")

# Live Kafka topic (rolling buffer of recent messages)
@canvas.stream()
def live():
    return ql.topic("f1-data", offset="latest", limit=200)

# Reactive Python cell — re-runs when its inputs change
@canvas.cell(viz={"type": "line", "x": "lap", "y": "lap_time_ms"})
def chart(laps):
    return laps

# Interactive widgets
@canvas.cell()
def driver():
    return ql.ui.dropdown(["tomas", "jana", "petr"], label="Driver")

@canvas.dataset()
def filtered(driver):
    return ql.sql(f"SELECT * FROM telemetry WHERE driver = '{driver}'")

if __name__ == "__main__":
    canvas.serve()
```

## Features

- **Persistent storage** — notebooks live on a 1 GB state volume mounted at `/app/state`, surviving restarts and redeploys.
- **Blob storage binding** — the workspace's blob storage is auto-mounted and accessible via `ql.StorageFile()` / `ql.StorageFolder()`.
- **Embedded plugin view** — appears as a top-level "QuixLab" item in the Quix sidebar and global menu.
- **Public access** — the canvas is reachable on port 80 of the deployment.

## Image

This template uses the prebuilt image
[`ghcr.io/quixio/quixlab`](https://github.com/quixio/quixlab/pkgs/container/quixlab).
The Dockerfile is a single `FROM` line — nothing else gets baked in.

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. For more information about QuixLab, visit the [QuixLab repo](https://github.com/quixio/quixlab).
