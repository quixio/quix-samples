# Tailscale Subnet Router for Quix

This container runs a Tailscale subnet router that allows secure connection to your Quix deployment from your private Tailscale network.

## Overview

This container runs a Tailscale subnet router in userspace networking mode, which allows you to:
- Connect to your Quix deployment securely via Tailscale
- Access internal services within your Quix deployment from your Tailscale network
- Route traffic between your Tailscale network and the Kubernetes cluster

## How to run

Create a [Quix](https://portal.platform.quix.io/signup?xlink=github) account or log in and visit the `Services` tab to deploy this service.

Clicking `Set up service` allows you to enter your connection details and runtime parameters.

Then either: 
* Click `Deploy` to deploy the pre-built and configured container into Quix.

* Or click `Customise service` to inspect or alter the code before deployment.

For optimal experience, read the `## Installation and Setting up of persistent storage` section below.

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
4. Persistent Storage set up when deploying this application

## Deployment Settings

When deploying this service, ensure you configure:
- DeploymentType: Service
- CPU: At least 200 millicores recommended
- Memory: At least 500MB recommended
- Replicas: 1 (multiple replicas are not needed for this service)
- Public Access: Not required

State preservation is important for maintaining the same Tailscale identity across pod restarts. The service automatically saves state to the `/app/state` directory.

## Installation and Setting up of persistent storage

In the Quix UI:
1. Click Templates (left-hand side)
2. Search for and select the Tailscale Subnet Router
3. Click Preview code just below the Description field to verify contents of the template
4. Click the TS_AUTHKEY field
5. Click + Secrets Management, add the field TS_AUTHKEY. Set **any** string as the value for either the default or the environment column
6. Save Changes, return to the Deployment
7. Click TS_AUTHKEY field again, and select the new secret called TS_AUTHKEY
8. Fill hostname and subnet values with your desired options
9. Click Deploy, wait for the deployment to finish
10. Go to deployments (left-hand column) and select your new subnet router deployment (it will have failed with runtime error)

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

In the Quix UI:
1. Looking at the Deployment's settings page, on the left-hand side click the field called TS_AUTHKEY, then Secrets Management
2. Paste the ts-authkey- value where we put the arbitrary string (either default or the field for the environment), click X on the Secrets Management panel
3. At the bottom of the `Edit deployment` panel, toggle `State Management` to true and choose the smallest available storage amount (1GB)
4. Click Redeploy

If done correctly, this will allow you to deploy and redeploy the application using the same `ts_hostname` you set.

## Troubleshooting

- If there are numbers attached to the end of your ts hostname in the Tailscale UI:
This happens because the nodekey isn't being persisted to State Storage in Quix. Ensure that the deployment has `State Management` enabled in the settings. Once toggled to true, delete unnecessary machines from Tailscale, generate a new TS_AUTHKEY, and redeploy the application.

## Notes

- The container saves the Tailscale machine and node keys for reuse to maintain the same identity even if the pod is restarted
- The container requires no special permissions in Kubernetes

## Open Source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.
