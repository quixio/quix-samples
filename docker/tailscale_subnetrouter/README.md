# Tailscale Subnet Router for Quix

This container runs a Tailscale subnet router that allows securely connecting to your Quix deployment from your private Tailscale network.

## Overview

This container runs a Tailscale subnet router in userspace networking mode, which allows you to:
- Connect to your Quix deployment securely via Tailscale
- Access internal services within your Quix deployment from your Tailscale network
- Route traffic between your Tailscale network and the Kubernetes cluster

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log-in and visit the `Services` tab to deploy this service.

Clicking `Set up service` allows you to enter your connection details and runtime parameters.

Then either: 
* click `Deploy` to deploy the pre-built and configured container into Quix.

* or click `Customise service` to inspect or alter the code before deployment.

## Environment Variables

The container supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TS_AUTHKEY` | **Required** Tailscale authentication key | - |
| `TAILSCALE_HOSTNAME` | Hostname for the Tailscale node | deployment name or "tailscale-subnetrouter" |
| `TAILSCALE_SUBNET` | **Required** Subnet CIDR to advertise (e.g. "10.128.0.0/9") | - |
| `TAILSCALE_STATE_DIR` | Directory to store Tailscale state files | /app/state |
| `TAILSCALE_SOCKS5_PORT` | Port for the SOCKS5 proxy | 1055 |
| `TAILSCALE_EXTRA_ARGS` | Additional arguments to pass to "tailscale up" command | "" |

## Usage

The container is designed to run as a service in Quix. It will:

1. Start tailscaled in userspace mode
2. Connect to your Tailscale network using the provided auth key
3. Advertise the specified subnet to your Tailscale network
4. Maintain the connection and restart if necessary

## Requirements / Prerequisites

You will need:
1. A Tailscale account and network set up
2. An authentication key generated from the Tailscale admin console
3. The subnet CIDR of your Quix deployment that you want to expose

## Deployment Settings

When deploying this service, ensure you configure:
- DeploymentType: Service
- CPU: At least 200 millicores recommended
- Memory: At least 500MB recommended
- Replicas: 1 (multiple replicas are not needed for this service)
- Public Access: Not required

State preservation is important for maintaining the same Tailscale identity across pod restarts. The service automatically saves state to the `/app/state` directory.

## Notes

- The container saves the Tailscale machine and node keys for reuse to maintain the same identity even if the pod is restarted
- The container requires no special permissions in Kubernetes

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.
