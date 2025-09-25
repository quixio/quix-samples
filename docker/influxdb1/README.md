# InfluxDB v1

This sample demonstrates how to deploy and use InfluxDB v1 as a time series database in your Quix Cloud pipeline. Please note: this image is provided by Influx and is offered as-is, with no specific support from Quix. For any support, contact Influx directly.

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Click `Deploy` to launch a pre-built container in Quix.
3. Configure authentication (username + password) for your InfluxDB instance:
    - `INFLUXDB_ADMIN_USER`: Admin username
    - `INFLUXDB_ADMIN_PASSWORD`: Admin password
    > Note: If non-empty username + password are provided, HTTP API authentication is also enabled
4. **\[Recommended, Optional\]** configure your DB name with the environment variable:   
    - `INFLUXDB_DB`: Database name to create (else, defaults to: `quix`)
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