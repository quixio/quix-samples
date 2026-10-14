#!/bin/bash
set -e

# Generates a fresh test CA and mosquitto server certificate on every run (not committed).
# The password file is committed and only generated if missing.

echo "Generating TLS certificates..."
mkdir -p certs

# openssl writes the keys as root with mode 0600, hence the chmod.
docker run --rm -v "$(pwd):/work" -w /work alpine:latest sh -c "
    apk add --no-cache openssl > /dev/null 2>&1 &&
    openssl genrsa -out certs/ca.key 2048 2>/dev/null &&
    openssl req -new -x509 -days 2 -key certs/ca.key -out certs/ca.crt -subj '/CN=Test CA' &&
    openssl genrsa -out certs/server.key 2048 2>/dev/null &&
    openssl req -new -key certs/server.key -out certs/server.csr -subj '/CN=mosquitto' -addext 'subjectAltName=DNS:mosquitto' &&
    openssl x509 -req -in certs/server.csr -CA certs/ca.crt -CAkey certs/ca.key -CAcreateserial -copy_extensions copy -out certs/server.crt -days 2 2>/dev/null &&
    rm certs/server.csr &&
    chmod 644 certs/ca.key certs/server.key
"

# Generate password file if it doesn't exist
if [ ! -f passwd ]; then
    echo "Generating password file..."
    echo "WARNING: Password file should be committed to git. This regeneration is for emergency use only."
    docker run --rm -v "$(pwd):/work" -w /work eclipse-mosquitto:2.0 mosquitto_passwd -c -b passwd testuser testpass
    echo "Password file generated. Please commit it to git."
else
    echo "Password file already exists (as expected)."
fi
