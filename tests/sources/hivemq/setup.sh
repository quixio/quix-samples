#!/bin/bash
set -e

# NOTE: This script is only needed if the test certificates and password file are missing.
# These files are now committed to git (they're test credentials, not real secrets).
# This script is kept for local development in case someone accidentally deletes them.

# Generate certificates if they don't exist
if [ ! -f certs/ca.crt ]; then
    echo "Generating TLS certificates..."
    echo "WARNING: Certificates should be committed to git. This regeneration is for emergency use only."
    mkdir -p certs

    # Use alpine with openssl to generate certificates
    docker run --rm -v "$(pwd):/work" -w /work alpine:latest sh -c "
        apk add --no-cache openssl > /dev/null 2>&1 &&
        openssl genrsa -out certs/ca.key 2048 2>/dev/null &&
        openssl req -new -x509 -days 365 -key certs/ca.key -out certs/ca.crt -subj '/CN=Test CA' &&
        openssl genrsa -out certs/server.key 2048 2>/dev/null &&
        openssl req -new -key certs/server.key -out certs/server.csr -subj '/CN=mosquitto' &&
        openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -out certs/server.crt -days 365 2>/dev/null &&
        rm certs/server.csr
    "

    echo "Certificates generated. Please commit them to git."
else
    echo "Certificates already exist (as expected)."
fi

# Generate password file if it doesn't exist
if [ ! -f passwd ]; then
    echo "Generating password file..."
    echo "WARNING: Password file should be committed to git. This regeneration is for emergency use only."
    docker run --rm -v "$(pwd):/work" -w /work eclipse-mosquitto:2.0 mosquitto_passwd -c -b passwd testuser testpass
    echo "Password file generated. Please commit it to git."
else
    echo "Password file already exists (as expected)."
fi
