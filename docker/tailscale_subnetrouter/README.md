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
| `TS_AUTHKEY` | **Required for initial setup only** Tailscale authentication key. After first setup with persistent storage, the auth key is no longer used as the identity is stored. | - |
| `TAILSCALE_HOSTNAME` | Hostname for the Tailscale node | deployment name or "tailscale-subnetrouter" |
| `TAILSCALE_SUBNET` | **Required** Subnet CIDR to advertise (e.g. "10.128.0.0/9") | - |
| `TAILSCALE_STATE_DIR` | Directory to store Tailscale state files | /app/state |
| `TAILSCALE_SOCKS5_PORT` | Port for the SOCKS5 proxy | 1055 |
| `TAILSCALE_EXTRA_ARGS` | Additional arguments to pass to "tailscale up" command | "" |

## Usage

The container is designed to run as a service in Quix. It will:

1. Start tailscaled in userspace mode
2. Check for existing identity in persistent storage
3. If identity exists, reconnect using stored credentials (without using the auth key)
4. If no identity exists, connect using the provided auth key and store the identity for future use
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

State preservation is important for maintaining the same Tailscale identity across pod restarts. The service automatically saves state to the `/app/state` directory.

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
4. Click the TS_AUTHKEY field
5. Click + Secrets Management, add the field TS_AUTHKEY and paste the authentication key from Tailscale (the one beginning with `ts-authkey-`)
6. Save Changes
7. Fill hostname and subnet values with your desired options
8. Click Deploy and wait for the deployment to finish

That's it! Your Tailscale Subnet Router is now deployed with state persistence enabled automatically. This allows you to deploy and redeploy the application using the same `ts_hostname` you set.

## Troubleshooting

- If there are numbers attached to the end of your ts hostname in the Tailscale UI:
This might happen if there was an issue with state persistence. If you're using a version of Quix that supports automatic state management (as configured in this template), this should not occur. If it does, please check the deployment logs for any errors.

- If you see authentication errors after redeploying:
This can happen if you're using a one-time auth key that has already been used. In this case, you may need to generate a new auth key in Tailscale, update the TS_AUTHKEY secret in Quix, and redeploy. With the updated script, this should only be necessary if the persistent storage was lost or the original stored identity was revoked.

## Notes

- The container saves the Tailscale machine and node keys for reuse to maintain the same identity even if the pod is restarted

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.
