# Tailscale Subnet Router for Quix

This container runs a Tailscale subnet router that allows secure connection to your Quix deployment from your private Tailscale network.

## Overview

This container runs a Tailscale subnet router in userspace networking mode, which allows you to:
- Connect to your Quix deployment securely via Tailscale
- Access internal services within your Quix deployment from your Tailscale network

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log in and visit the `Services` tab to deploy this service.

Clicking `Set up service` allows you to enter your connection details and runtime parameters.

Then either: 
* Click `Deploy` to deploy the pre-built and configured container into Quix.

* Or click `Customise service` to inspect or alter the code before deployment.

The service comes pre-configured with state persistence enabled for optimal experience.

## Environment Variables

The container supports the following environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `TS_AUTHKEY` | **Required for initial setup only** Tailscale authentication key. After first setup with persistent storage, the auth key is no longer needed as the identity is stored in state. | - |
| `TAILSCALE_HOSTNAME` | Hostname for the Tailscale node | deployment name or "tailscale-subnetrouter" |
| `TAILSCALE_SUBNET` | **Required** Subnet CIDR to advertise (e.g. "10.128.0.0/9") | - |
| `TAILSCALE_STATE_DIR` | Directory to store Tailscale state files | /app/state |
| `TAILSCALE_SOCKS5_PORT` | Port for the SOCKS5 proxy | 1055 |
| `TAILSCALE_EXTRA_ARGS` | Additional arguments to pass to "tailscale up" command | "" |

## Usage

The container is designed to run as a service in Quix. It will:

1. Start tailscaled in userspace mode with the persistent state directory
2. Check if valid Tailscale state exists in the persistent storage
3. If valid state exists, attempt to reconnect using the stored state (without using the auth key)
4. If reconnection fails or no valid state exists, try to connect using the provided auth key
5. Advertise the specified subnet to your Tailscale network
6. Maintain the connection and restart if necessary

## Requirements / Prerequisites

You will need:
1. A Tailscale account and network set up
2. An authentication key generated from the Tailscale admin console (ephemeral key recommended)
3. The subnet CIDR of your Quix deployment that you want to expose

## Deployment Settings

When deploying this service, the following settings are pre-configured:
- DeploymentType: Service
- CPU: 200 millicores
- Memory: 500MB
- Replicas: 1 (multiple replicas are not needed for this service)
- Public Access: Not required
- State Management: Enabled (1GB)

State preservation is important for maintaining the same Tailscale identity across pod restarts. The service automatically saves all Tailscale state to the `/app/state/ts` directory.

## How State Persistence Works

For effective state persistence, the container needs to properly store and retrieve Tailscale identity information:

1. **Initial deployment**: Requires a valid auth key to authenticate with Tailscale
2. **State creation**: Upon successful authentication, Tailscale automatically stores its state
3. **Subsequent restarts**: The container checks for valid state files:
   - Looking for a sufficiently-sized state file (>100 bytes)
   - Checking for the existence of nodekey and machinekey files
4. **If valid state exists**: The container will attempt to reconnect without using the auth key
5. **If state is invalid/missing**: Falls back to auth key authentication

This approach ensures that the same Tailscale identity is maintained as long as the persistent volume is preserved.

## Installation

### Step 1: Setup in Tailscale

In the Tailscale UI:
1. Click ACLs tab, add the following tag to your ACL JSON definition
```json
	"tagOwners": {
		"tag:subnet-router": ["autogroup:admin"],
	},
	"acls": [
		{"action": "accept", "src": ["*"], "dst": ["*:*"]},
	],
	"autoApprovers": {
		"routes": {
			"10.128.0.0/9": ["tag:subnet-router"],
		},
	},
```
This will define a tag called `subnet-router`, which you may change as you wish. It will also set this tag up to allow the automatic acceptance of the subnet route your new Tailscale Subnet Router application will export to your Tailscale network. If you require tighter Access Control, you may set these under the `acls` key.

2. Once the new ACLs are applied, navigate back to the `Machines` tab, click `Add Device` and choose Linux server
3. For Tags, choose `tag:subnet-router` or your chosen name, and any additional tags you require
4. Enable toggle for `Ephemeral`
5. Scroll down the page, click `Generate install script`
6. Copy the authentication key, it begins with `ts-authkey-`

### Step 2: Deploy in Quix

In the Quix UI:
1. Click Services (left-hand side)
2. Search for and select the Tailscale Subnet Router
3. Click the TS_AUTHKEY field
4. Click + Secrets Management, add the field TS_AUTHKEY and paste the authentication key from Tailscale (the one beginning with `ts-authkey-`)
5. Save Changes
6. Fill hostname and subnet values with your desired options
7. Click Deploy and wait for the deployment to finish

That's it! Your Tailscale Subnet Router is now deployed with state persistence enabled automatically. This allows you to maintain the same Tailscale identity even when redeploying the service.

## Troubleshooting

### Authentication Issues

- **If you see an interactive authentication URL in the logs**:
  This happens if the service can't automatically authenticate. Check if:
  1. Your auth key might have expired or been already used (Tailscale auth keys are often one-time use)
  2. There might be an issue with the persistent storage
  3. The state files might exist but be invalid or incomplete
  
  **Solution**: Generate a new auth key in Tailscale, update the TS_AUTHKEY secret in Quix, and redeploy.

- **If there are numbers attached to the end of your ts hostname in the Tailscale UI**:
  This indicates that a new Tailscale identity was created instead of reusing the previous one.
  
  **Solution**: Ensure state persistence is working by checking the deployment logs. If you need to, delete the redundant machine from Tailscale, update your auth key, and redeploy.

### Persistent Storage Issues

- **If state isn't persisting between restarts**:
  1. Verify that the State configuration is enabled in the deployment settings
  2. Check that the filesystem is writable by the container
  3. Check logs for any permission errors
  4. Inspect the state directory contents with `ls -la /app/state/ts`
  
  The Tailscale state is stored in the `/app/state/ts` directory and should contain several files including `tailscaled.state`, `nodekey`, and `machinekey`.

- **If you see "state file is missing or too small" in logs**:
  This means that the state file exists but doesn't contain valid data. It might have been truncated or corrupted.
  
  **Solution**: Delete the existing files in the state directory (if possible) or redeploy with a new auth key.

## Notes

- The container uses Tailscale's built-in state management to maintain identity
- The script performs validation on state files to ensure they're not just present but actually valid
- No special privileges are required to run the container

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.
