#!/bin/bash
set -e

# Generate certificates if they don't exist
if [ ! -f certs/ca.crt ]; then
    echo "Generating TLS certificates..."
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

    echo "Certificates generated"
fi

# Generate password file if it doesn't exist
if [ ! -f passwd ]; then
    echo "Generating password file..."
    docker run --rm -v "$(pwd):/work" -w /work eclipse-mosquitto:2.0 mosquitto_passwd -c -b passwd testuser testpass
    echo "Password file generated"
fi
