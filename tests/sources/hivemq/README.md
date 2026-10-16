# HiveMQ Source Test

This test verifies the HiveMQ MQTT source connector with TLS authentication.

## Test Certificates and Credentials

The `certs/` directory and `passwd` file contain **test credentials only** (not real secrets).

### Files
- `certs/ca.crt`, `certs/ca.key` - Test Certificate Authority
- `certs/server.crt`, `certs/server.key` - Mosquitto server certificate (`CN=mosquitto`, `subjectAltName=DNS:mosquitto`)
- `passwd` - Mosquitto password file (user: testuser, pass: testpass)

### Generation

`setup.sh` runs before every test and generates a fresh CA and server certificate in `certs/`
using docker, valid for 2 days. `certs/` is gitignored.

`passwd` is committed. `setup.sh` regenerates it only if it is missing; commit it again if that happens.
