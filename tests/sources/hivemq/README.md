# HiveMQ Source Test

This test verifies the HiveMQ MQTT source connector with TLS authentication.

## Test Certificates and Credentials

The `certs/` directory and `passwd` file contain **test credentials only** (not real secrets).
They are committed to git to avoid needing docker during CI setup.

### Files
- `certs/ca.crt`, `certs/ca.key` - Test Certificate Authority
- `certs/server.crt`, `certs/server.key` - Mosquitto server certificates
- `passwd` - Mosquitto password file (user: testuser, pass: testpass)

### Regenerating (if needed)

If you accidentally delete these files, run:

```bash
./setup.sh
```

This will regenerate them using docker. After regeneration, commit them to git.

**Note:** The setup.sh script is kept only for emergency regeneration. In normal operation,
the committed certificates are used directly and setup.sh just verifies they exist.
