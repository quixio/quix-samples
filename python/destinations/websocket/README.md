# WebSocket Destination

A service that streams data from a Quix input stream to connected WebSocket clients.

## Overview

This service receives data from a Quix input stream and forwards it to all connected WebSocket clients. It acts as a bridge between Quix and any application that can consume WebSocket data.

## Configuration

The service requires the following environment variables:

| Variable | Description |
|----------|-------------|
| `input` | The input topic name to listen to in Quix |
| `PORT` | The port to host the WebSocket server on (default: 8000) |
| `AUTH_ENABLED` | Enable/disable authentication (values: "true"/"false") |
| `AUTH_API_KEYS` | Comma-separated list of allowed API keys when authentication is enabled |

## Authentication

Authentication can be enabled or disabled using the `AUTH_ENABLED` environment variable:

- When `AUTH_ENABLED=true`: Clients must provide a valid API key as a query parameter
- When `AUTH_ENABLED=false`: No authentication is required to connect

### Connecting with Authentication

When authentication is enabled, clients must connect with an API key passed as a query parameter:

```
ws://your-server:8000/ws?token=your_api_key
```

The API key must match one of the keys specified in the `AUTH_API_KEYS` environment variable.

### Managing API Keys

API keys are defined in the `AUTH_API_KEYS` environment variable as a comma-separated list:

```
AUTH_API_KEYS=key1,key2,secret_key_3
```

Each client must use one of these keys in their connection request to be authenticated.

## Usage

### Connecting to the WebSocket

Connect to the WebSocket endpoint at:

```
ws://your-server:8000/ws
```

If authentication is enabled, include your API key:

```
ws://your-server:8000/ws?token=your_api_key
```

### Data Format

Data is sent as JSON strings over the WebSocket connection. The format mirrors the structure received from Quix, including timestamp, tag names, and values.

### Example Client Code

Here's a simple JavaScript example of connecting to the WebSocket:

```javascript
// Connect to WebSocket with authentication
const socket = new WebSocket('ws://your-server:8000/ws?token=your_api_key');

// Handle incoming data
socket.onmessage = function(event) {
  const data = JSON.parse(event.data);
  console.log('Received data:', data);
};

// Handle connection open
socket.onopen = function(event) {
  console.log('Connected to WebSocket server');
};

// Handle errors
socket.onerror = function(error) {
  console.error('WebSocket Error:', error);
};

// Handle connection close
socket.onclose = function(event) {
  console.log('Disconnected from WebSocket server');
};
```

## Running Locally

1. Set up the required environment variables
2. Install dependencies: `pip install -r requirements.txt`
3. Run the service: `python main.py`

## Deploying to Quix

This sample can be deployed directly to your Quix environment.

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in to your existing environment and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix. 

* or click `Customise connector` to inspect or alter the code before deployment.

## Limitations

- The service does not support bidirectional communication - it only sends data from Quix to WebSocket clients
- WebSocket connections without a valid token will be immediately closed when authentication is enabled

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Please star us and mention us on social to show your appreciation.

