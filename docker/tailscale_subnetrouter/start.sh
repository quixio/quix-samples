#!/bin/bash
set -e

# Directory for Tailscale state - can be overridden with env var
STATE_DIR=${TAILSCALE_STATE_DIR:-"/app/state"}
MACHINE_KEY_FILE="$STATE_DIR/machine_key"
NODE_KEY_FILE="$STATE_DIR/node_key"

# Create state directory if it doesn't exist
mkdir -p $STATE_DIR

# Get hostname from environment variable or deployment name
HOSTNAME=${TAILSCALE_HOSTNAME:-${Quix__Deployment__Name:-"tailscale-subnetrouter"}}
# Clean the hostname for Tailscale use
HOSTNAME_CLEAN=$(echo "$HOSTNAME" | tr ' ' '-' | tr -cd '[:alnum:]-')

# SOCKS5 proxy port - can be overridden with env var
SOCKS5_PORT=${TAILSCALE_SOCKS5_PORT:-1055}

echo "Starting Tailscale subnet router in userspace mode..."

# Check if we have existing keys
if [ -f "$MACHINE_KEY_FILE" ] && [ -f "$NODE_KEY_FILE" ]; then
    echo "Found existing Tailscale keys, reusing previous identity..."
    export TS_USERSPACE_ROUTER=true
    export TS_MACHINE_KEY=$(cat "$MACHINE_KEY_FILE")
    export TS_NODE_KEY=$(cat "$NODE_KEY_FILE")
    
    # Start tailscaled with existing keys
    /usr/sbin/tailscaled --tun=userspace-networking --statedir=$STATE_DIR --socks5-server=0.0.0.0:$SOCKS5_PORT &
    
    TAILSCALED_PID=$!
    
    # Wait for tailscaled to initialize
    sleep 2
    
    echo "Reconnecting to Tailscale network with existing identity..."
    
    # Additional Tailscale options if provided
    TAILSCALE_EXTRA_ARGS=${TAILSCALE_EXTRA_ARGS:-""}
    
    # When we have existing keys, we don't need to use the authkey again
    # Just connect with the stored identity and advertise routes
    /usr/bin/tailscale up --hostname="$HOSTNAME_CLEAN" --advertise-routes="$TAILSCALE_SUBNET" $TAILSCALE_EXTRA_ARGS
else
    echo "No existing keys found, starting with fresh identity..."
    # Start tailscaled without existing keys
    /usr/sbin/tailscaled --tun=userspace-networking --statedir=$STATE_DIR --socks5-server=0.0.0.0:$SOCKS5_PORT --state=mem: &
    
    TAILSCALED_PID=$!
    
    # Wait for tailscaled to initialize
    sleep 2
    
    # Check if TS_AUTHKEY environment variable exists
    if [ -n "$TS_AUTHKEY" ]; then
        echo "Connecting to Tailscale network with auth key..."
        
        # Additional Tailscale options if provided
        TAILSCALE_EXTRA_ARGS=${TAILSCALE_EXTRA_ARGS:-""}
        
        # Connect to Tailscale using the auth key for new setup
        /usr/bin/tailscale up --authkey="$TS_AUTHKEY" --hostname="$HOSTNAME_CLEAN" --advertise-routes="$TAILSCALE_SUBNET" $TAILSCALE_EXTRA_ARGS
        
        # Save machine and node keys for future pod recreations
        echo "Saving Tailscale keys for reuse..."
        /usr/bin/tailscale status --json | jq -r .MachineKey > "$MACHINE_KEY_FILE"
        /usr/bin/tailscale status --json | jq -r .NodeKey > "$NODE_KEY_FILE"
        # Secure the keys
        chmod 600 "$MACHINE_KEY_FILE" "$NODE_KEY_FILE"
    else
        echo "TS_AUTHKEY not found. Tailscale cannot be authenticated."
        kill $TAILSCALED_PID 2>/dev/null || true
        exit 1
    fi
fi

echo "Tailscale connected successfully"
echo "Tailscale IP: $(/usr/bin/tailscale ip -4)"
echo "======== service domain suffix =============="
echo ".$(grep search /etc/resolv.conf | awk '{print $2}' | sed 's/^svc.//')"

# Instead of sleeping, monitor tailscaled process
echo "Tailscale subnet router is running. Monitoring tailscaled..."

# Trap for cleanup
trap 'kill $TAILSCALED_PID 2>/dev/null || true; echo "Shutting down tailscale..."; sleep 1; exit 0' TERM INT

# Wait for tailscaled process - this replaces "sleep infinity"
wait $TAILSCALED_PID