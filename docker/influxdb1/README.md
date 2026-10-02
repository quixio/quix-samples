# InfluxDB v1

This sample demonstrates how to deploy and use InfluxDB v1 as a time series database in your Quix Cloud pipeline. Please note: this image is provided by Influx and is offered as-is, with no specific support from Quix. For any support, contact Influx directly.

## Configuration

This sample uses the shared **`influxdb1-config`** variable group, so the server and every
client (source/sink) read the same connection details and credentials. Assign the group to
this deployment (or your project/environment) with:

- **INFLUXDB1_HOST** — host address clients use to reach the server, including the scheme (default `http://influxdb`)
- **INFLUXDB1_PORT** — port clients connect on (default `80`, which maps to 8086 in the container)
- **INFLUXDB1_DATABASE** — database the server is initialised with, and that clients read and write (default `quix`)
- **INFLUXDB1_USERNAME** — admin username the server is initialised with (default `admin`)
- **INFLUXDB1_PASSWORD** — admin password for that user, secret

If a non-empty username and password are provided, HTTP API authentication is enabled. The
v1 image reads `INFLUXDB_ADMIN_USER` / `INFLUXDB_ADMIN_PASSWORD` / `INFLUXDB_DB`; `init.sh`
maps the group values onto those names, and falls back to them directly so deployments
created before the group was introduced keep working.

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Click `Deploy` to launch a pre-built container in Quix.
3. Assign the `influxdb1-config` variable group and set authentication (username + password) for your InfluxDB instance:
    - `INFLUXDB1_USERNAME`: Admin username
    - `INFLUXDB1_PASSWORD`: Admin password
    > Note: If non-empty username + password are provided, HTTP API authentication is also enabled
4. **\[Recommended, Optional\]** configure your DB name in the same group:   
    - `INFLUXDB1_DATABASE`: Database name to create (else, defaults to: `quix`)
5. **\[Recommended, Optional\]** Enable state, otherwise changes will be lost on restart.  
    > Note: the necessary storage type may not be supported on all Quix Platforms.

## How to Use

To interact with InfluxDB v1 from your pipeline, add influxdb to your requirements.txt file and use the following Python code:

```python
from influxdb import InfluxDBClient

# Configure client settings
host = "influxdb"
port = 8086
username = "admin"  # your admin username
password = "your-password"  # your admin password
database = "quix"  # your database name

# Connect to InfluxDB v1
client = InfluxDBClient(host=host, port=port, username=username, password=password, database=database)

# Write a data point
json_body = [
    {
        "measurement": "temperature",
        "tags": {
            "host": "server01",
            "region": "us-west"
        },
        "fields": {
            "value": 25.3
        }
    }
]
client.write_points(json_body)

# Query data from the last hour
query = 'SELECT * FROM temperature WHERE time > now() - 1h'
result = client.query(query)
for point in result.get_points():
    print(point)

client.close()
```

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no InfluxDB specific support from Quix.