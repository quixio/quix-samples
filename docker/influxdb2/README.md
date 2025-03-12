# InfluxDB v2

This sample demonstrates how to deploy and use InfluxDB v2 as a time series database in your Quix Cloud pipeline. Please note: this image is provided by Influx and is offered as-is, with no specific support from Quix. For any support, contact Influx directly.

## How to Run

1. Create an account or log in to your [Quix](https://portal.platform.quix.io/signup?xlink=github) account and navigate to the Code Samples section.
2. Click `Deploy` to launch a pre-built container in Quix.
3. Complete the required environment variables to configure your InfluxDB instance.

After deploying InfluxDB v2 to your pipeline, edit the pipeline YAML to add the necessary network configuration:

- Click the `YAML` button in the top right of the pipeline view.
- Click `Edit code` near the top right of the displayed YAML code.
- Locate the `deployments` section of the YAML.
- Find the `influxdb` deployment (e.g. look for `- name: influxdb`).
- Add the snippet below under `resources` (ensure `network` is at the same level as `resources`):

```yaml
network:
  serviceName: influxdb
  ports:
    - port: 8086
      targetPort: 8086
```
The complete deployment entry for InfluxDB v2 should resemble:
```yaml
deployments:
  - name: influxdb
    application: influxdb
    version: latest
    deploymentType: Service
    resources:
      cpu: 1000
      memory: 8000
      replicas: 1
    network:
      serviceName: influxdb
      ports:
        - port: 8086
          targetPort: 8086
```

Once you’ve updated the YAML, click the blue Sync environment button and then select Sync to this commit on the popup. Your updated configuration will be applied, and the InfluxDB service will restart.

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

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no specific support from Quix.