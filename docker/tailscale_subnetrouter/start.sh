#!/bin/bash
set -e

echo "=== Tailscale Subnet Router Startup ==="

# Directory for Tailscale state - can be overridden with env var
STATE_DIR=${TAILSCALE_STATE_DIR:-"/app/state"}
TS_STATE_DIR="$STATE_DIR/ts"  # Directory to store tailscale state files

echo "STATE_DIR: $STATE_DIR"
echo "TS_STATE_DIR: $TS_STATE_DIR"

# Create state directories if they don't exist
mkdir -p "$STATE_DIR"
mkdir -p "$TS_STATE_DIR"
echo "State directories created/verified"

# Get hostname from environment variable or deployment name
HOSTNAME=${TAILSCALE_HOSTNAME:-${Quix__Deployment__Name:-"tailscale-subnetrouter"}}
# Clean the hostname for Tailscale use
HOSTNAME_CLEAN=$(echo "$HOSTNAME" | tr ' ' '-' | tr -cd '[:alnum:]-')
echo "Using hostname: $HOSTNAME_CLEAN"

# SOCKS5 proxy port - can be overridden with env var
SOCKS5_PORT=${TAILSCALE_SOCKS5_PORT:-1055}
echo "SOCKS5 proxy port: $SOCKS5_PORT"

# Validate TAILSCALE_SUBNET is set
if [ -z "$TAILSCALE_SUBNET" ]; then
    echo "ERROR: TAILSCALE_SUBNET environment variable is not set. This is required."
    exit 1
fi
echo "Using subnet: $TAILSCALE_SUBNET"

# Prepare extra args if provided
if [ -n "$TAILSCALE_EXTRA_ARGS" ]; then
    echo "Extra args provided: $TAILSCALE_EXTRA_ARGS"
    # Split extra args into an array for proper handling
    read -ra EXTRA_ARGS <<< "$TAILSCALE_EXTRA_ARGS"
else
    EXTRA_ARGS=()
    echo "No extra args provided"
fi

echo "Starting Tailscale subnet router in userspace mode..."

# Start tailscaled with the state directory
# The statefulness is handled by tailscaled reading directly from the state dir
/usr/sbin/tailscaled --tun=userspace-networking --statedir="$TS_STATE_DIR" --socks5-server=0.0.0.0:$SOCKS5_PORT &

TAILSCALED_PID=$!
echo "Tailscaled started with PID: $TAILSCALED_PID"

# Wait for tailscaled to initialize
echo "Waiting for tailscaled to initialize..."
sleep 2

# Check for state directory contents
echo "Checking for existing state in $TS_STATE_DIR..."
if [ -d "$TS_STATE_DIR" ] && ls -la "$TS_STATE_DIR"; then
    echo "Directory content shown above"
else
    echo "Error listing directory contents"
fi

# Check if we have existing state
if [ -d "$TS_STATE_DIR" ] && [ -n "$(ls -A "$TS_STATE_DIR" 2>/dev/null)" ]; then
    echo "Found existing Tailscale state, attempting to reuse previous identity..."
    
    # Try to connect without auth key using the existing state
    echo "Reconnecting with existing state..."
    if /usr/bin/tailscale up --hostname="$HOSTNAME_CLEAN" --advertise-routes="$TAILSCALE_SUBNET" "${EXTRA_ARGS[@]}"; then
        echo "Successfully reconnected with existing identity!"
    else
        echo "Failed to reconnect with existing identity. Will try using auth key if available."
        
        # Check if TS_AUTHKEY environment variable exists for fallback
        if [ -n "$TS_AUTHKEY" ]; then
            echo "Using auth key as fallback..."
            if /usr/bin/tailscale up --authkey="$TS_AUTHKEY" --hostname="$HOSTNAME_CLEAN" --advertise-routes="$TAILSCALE_SUBNET" "${EXTRA_ARGS[@]}"; then
                echo "Successfully authenticated with auth key"
            else
                echo "Failed to authenticate with auth key"
            fi
        else
            echo "No TS_AUTHKEY provided for fallback authentication. Check the interactive URL below."
        fi
    fi
else
    echo "No existing state found, starting with fresh identity..."
    
    # Check if TS_AUTHKEY environment variable exists
    if [ -n "$TS_AUTHKEY" ]; then
        echo "Connecting to Tailscale network with auth key..."
        
        # Connect to Tailscale using the auth key for new setup
        if /usr/bin/tailscale up --authkey="$TS_AUTHKEY" --hostname="$HOSTNAME_CLEAN" --advertise-routes="$TAILSCALE_SUBNET" "${EXTRA_ARGS[@]}"; then
            echo "Successfully authenticated with auth key"
        else
            echo "Failed to authenticate with auth key"
        fi
    else
        echo "TS_AUTHKEY not found. Please authenticate using the URL below."
    fi
fi

# Check connection status
echo "Checking Tailscale connection status..."
if TAILSCALE_IP=$(/usr/bin/tailscale ip -4 2>/dev/null); then
    echo "Tailscale connected successfully"
    echo "Tailscale IP: $TAILSCALE_IP"
    echo "======== service domain suffix =============="
    echo ".$(grep search /etc/resolv.conf | awk '{print $2}' | sed 's/^svc.//')"
    
    # Show more details
    echo "Tailscale status:"
    /usr/bin/tailscale status
else
    echo "Tailscale not yet fully connected. Check logs for authentication URL if needed."
    echo "Tailscale status attempt:"
    /usr/bin/tailscale status || echo "Failed to get status"
fi

# Instead of sleeping, monitor tailscaled process
echo "Tailscale subnet router is running. Monitoring tailscaled..."

# Trap for cleanup
trap 'kill $TAILSCALED_PID 2>/dev/null || true; echo "Shutting down tailscale..."; sleep 1; exit 0' TERM INT

# Wait for tailscaled process - this replaces "sleep infinity"
wait $TAILSCALED_PID