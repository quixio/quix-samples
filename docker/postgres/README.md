# PostgreSQL

This sample demonstrates how to deploy and use a PostgreSQL database in your Quix Cloud pipeline. 

Please note: this image is provided by Postgres and is offered as-is, with no specific support from Quix. For any support, contact Postgres directly.

## Configuration

This sample uses the shared **`postgres-connection`** variable group, so the server and
every client (sink, CDC source) read the same connection details. Assign the group to this
deployment (or your project/environment) with:

- **POSTGRES_HOST** — host address clients use to reach the server (default `postgresql`, the internal service name)
- **POSTGRES_PORT** — port clients connect on (default `80`, which maps to 5432 in the container)
- **POSTGRES_DB** — database the server is initialised with, and that clients connect to (default `quix`)
- **POSTGRES_USER** — root username the server is initialised with (default `admin`)
- **POSTGRES_PASSWORD** — root password for that user, secret

The postgres image reads `POSTGRES_USER`, `POSTGRES_PASSWORD` and `POSTGRES_DB` under
exactly those names, so the group values reach it directly with no mapping.

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Assign the `postgres-connection` variable group, setting at least `POSTGRES_PASSWORD`.
3. Click `Deploy` to launch a pre-built container in Quix.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## How to Use
To interact with PosgreSQL from your pipeline, either use one of the no-code [PostgreSQL connectors](https://quix.io/integrations?category=SQL+DB)
in Quix Cloud or use a Quix Streams [PostgreSQLSink](https://quix.io/docs/quix-streams/connectors/sinks/postgresql-sink.html) directly.

Assign the same `postgres-connection` variable group to those clients so they connect with
the matching host, port, database and credentials — no need to copy the values by hand:
```shell
host="$POSTGRES_HOST"          # default "postgresql"
port="$POSTGRES_PORT"          # default 80
username="$POSTGRES_USER"      # default "admin"
password="$POSTGRES_PASSWORD"
db="$POSTGRES_DB"              # default "quix"
```

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no InfluxDB specific support from Quix.