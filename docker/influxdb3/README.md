# InfluxDB v3 (alpha)

This sample demonstrates how to deploy and use InfluxDB v3 as a time series database in your Quix Cloud pipeline. 

Please note: this image is provided by Influx and is offered as-is, with no specific support from Quix. For any support, contact Influx directly.

[!WARNING]
This offering is currently in alpha and intended only for simple testing/validation, 
especially since authentication is not set up. 
Only local file storage is supported in this implementation.

You can learn more about InfluxDB3 [from their documentation](https://docs.influxdata.com/influxdb3/core/).

## How to Run

1. Create an account or log in to your [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account and navigate to the Code Samples section.
2. Click `Deploy` to launch a pre-built container in Quix.
3. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## How to Use
To interact with InfluxDB v3 from your pipeline, either use one of the no-code [influxdb3 connectors](https://quix.io/integrations?category=Time+series+DB)
in Quix Cloud or use a Quix Streams [InfluxDBSource](https://quix.io/docs/quix-streams/connectors/sources/influxdb3-source.html) or [InfluxDB3Sink](https://quix.io/docs/quix-streams/connectors/sinks/influxdb3-sink.html) directly.

Use the following values to connect:
```shell
host="http://influxdb3"
organization_id="<ANYTHING>"  # required, but not used
token="<ANYTHING>"            # required, but not used
```

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Influx and is offered as-is, with no InfluxDB specific support from Quix.