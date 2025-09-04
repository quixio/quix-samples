# PostgreSQL

This sample demonstrates how to deploy and use a PostgreSQL database in your Quix Cloud pipeline. 

Please note: this image is provided by Postgres and is offered as-is, with no specific support from Quix. For any support, contact Postgres directly.

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Click `Deploy` to launch a pre-built container in Quix.
3. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## How to Use
To interact with PosgreSQL from your pipeline, either use one of the no-code [PostgreSQL connectors](https://quix.io/integrations?category=SQL+DB)
in Quix Cloud or use a Quix Streams [PostgreSQLSink](https://quix.io/docs/quix-streams/connectors/sinks/postgresql-sink.html) directly.

Use the following values to connect:
```shell
host="postgresql"
port=80
username="admin"  # or your POSTGRES_USER value
password="<YOUR PASSWORD>" # your POSTGRES_PASSWORD value
db="quix"  # or your POSTGRES_DB value
```

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no InfluxDB specific support from Quix.