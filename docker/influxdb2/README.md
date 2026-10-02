# InfluxDB v2

This sample demonstrates how to deploy and use InfluxDB v2 as a time series database in your Quix Cloud pipeline. Please note: this image is provided by Influx and is offered as-is, with no specific support from Quix. For any support, contact Influx directly.

## Configuration

This sample uses the shared **`influxdb2-config`** variable group, so the server, the
InfluxDB v2 Source and Grafana all read the same connection details and token. Assign the
group to this deployment (or your project/environment) with:

- **INFLUXDB2_HOST** — base URL clients use to reach the server, including scheme and port (default `http://influxdb:80`)
- **INFLUXDB2_TOKEN** — admin token, secret. Seeds server auth on first boot and authenticates clients
- **INFLUXDB2_ORG** — organization the server is initialised with, and that clients query (default `quix`)
- **INFLUXDB2_BUCKET** — bucket the server is initialised with, and that clients read and write (default `demo`)
- **INFLUXDB2_USERNAME** — admin username the server is initialised with (default `admin`)
- **INFLUXDB2_PASSWORD** — admin password for that user, secret

The v2 image is set up from `DOCKER_INFLUXDB_INIT_*`; `init.sh` maps the group values onto
those names, and falls back to them directly so deployments created before the group was
introduced keep working.

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Click `Deploy` to launch a pre-built container in Quix.
3. Assign the `influxdb2-config` variable group, setting at least `INFLUXDB2_TOKEN` and `INFLUXDB2_PASSWORD`.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## How to Use
To interact with InfluxDB v2 from your pipeline, add influxdb-client to your requirements.txt file and use the following Python code:

```python
import influxdb_client
from influxdb_client.client.write_api import SYNCHRONOUS

# Configure client settings
token = "your-token"
org = "your-org"
bucket = "your-bucket"

# Connect to InfluxDB v2
client = influxdb_client.InfluxDBClient(url="http://influxdb:8086", token=token, org=org)

# Write a data point
write_api = client.write_api(write_options=SYNCHRONOUS)
point = (
    influxdb_client.Point("measurement_name")
    .tag("tag_key", "tag_value")
    .field("field_key", 10)
)
write_api.write(bucket, org, point)

# Query data from the last hour
query = f'from(bucket:"{bucket}") |> range(start: -1h)'
tables = client.query_api().query(query, org=org)
for table in tables:
    for record in table.records:
        print(record)

client.close()
```

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no InfluxDB specific support from Quix.