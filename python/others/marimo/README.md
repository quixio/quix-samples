# Marimo

This sample demonstrates how to deploy a [Marimo](https://marimo.io/) notebook instance, a reactive Python notebook environment, on the Quix platform.

## How to Run

1. Log in or sign up at [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Fill in the required environment variables for your Marimo instance.
4. Enable state management to persist your notebooks across restarts.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MARIMO_MODE` | Notebook mode: `browser` (file browser), `edit` (edit specific notebook), or `run` (run specific notebook) | `browser` |
| `MARIMO_NOTEBOOK` | Notebook file to open (used with `edit` or `run` modes) | `main.py` |
| `MARIMO_PASSWORD` | Optional password protection for standalone mode | (none) |
| `QUIX_PLUGIN_MODE` | Set to `true` to enable Quix plugin mode with nginx auth proxy | `false` |

## Modes

- **Standalone mode** (`QUIX_PLUGIN_MODE=false`): Direct access to Marimo on port 8080. Supports optional password protection via `MARIMO_PASSWORD`.
- **Plugin mode** (`QUIX_PLUGIN_MODE=true`): Runs behind nginx with Quix authentication proxy for secure access within the Quix platform.

## Features

- Dark theme enabled by default
- Auto-save with 1 second delay
- Code completion on typing
- Persistent state directory at `/app/state`

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. For more information about Marimo, visit [marimo.io](https://marimo.io/).
