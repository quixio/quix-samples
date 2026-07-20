# InfluxDB v3 (alpha)

This sample demonstrates how to deploy and use InfluxDB v3 as a time series database in your Quix Cloud pipeline. 

Please note: this image is provided by Influx and is offered as-is, with no specific support from Quix. For any support, contact Influx directly.

[!WARNING]
This offering is currently in alpha and intended only for simple testing/validation.
Only local file storage is supported in this implementation.

You can learn more about InfluxDB3 [from their documentation](https://docs.influxdata.com/influxdb3/core/).

## Configuration

This sample uses the shared **`influxdb3-config`** variable group, so the server and
every client (source/sink) read the same connection details and token. Assign the group
to this deployment (or your project/environment) with:

- **INFLUXDB3_HOST** — base URL clients use to reach the server (default `http://influxdb3`)
- **INFLUXDB3_TOKEN** — admin token, secret, **optional**. If set it must start with `apiv3_`; it seeds server auth on first boot and authenticates clients. **Leave it blank to run the server without authentication** (the original alpha behaviour).
- **INFLUXDB3_DATABASE** — default database clients read/write (default `quix`)
- **INFLUXDB3_ORG** — organization id; required by some clients (e.g. Quix Streams) but not used by InfluxDB 3 Core (default `quix`)

The container also reads two optional standalone overrides: `INFLUXDB3_NODE_ID` (default `node0`)
and `INFLUXDB3_OBJECT_STORE` (default `file`).

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Assign the `influxdb3-config` variable group. Optionally set `INFLUXDB3_TOKEN` (a value starting with `apiv3_`) to enable authentication; leave it blank to run without auth.
3. Click `Deploy` to launch a pre-built container in Quix.
4. Enable state, otherwise changes (including the seeded admin token) will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## How to Use
To interact with InfluxDB v3 from your pipeline, either use one of the no-code [influxdb3 connectors](https://quix.io/integrations?category=Time+series+DB)
in Quix Cloud or use a Quix Streams [InfluxDBSource](https://quix.io/docs/quix-streams/connectors/sources/influxdb3-source.html) or [InfluxDB3Sink](https://quix.io/docs/quix-streams/connectors/sinks/influxdb3-sink.html) directly.

Assign the same `influxdb3-config` variable group to those clients so they connect with the
matching host, token, database and org — no need to copy the values by hand.

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no InfluxDB specific support from Quix.