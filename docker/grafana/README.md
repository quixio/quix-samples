# Grafana

This sample demonstrates how to deploy and use Grafana as a visualization tool in your Quix Cloud pipeline. Please note: this image is provided by Grafana and is offered as-is, with no specific support from Quix.

## Configuration

- **GF_SECURITY_ADMIN_PASSWORD** — password for the Grafana admin user, secret.

The provisioned InfluxDB datasource takes its token from the shared
**`influxdb2-config`** variable group, so Grafana, the bundled InfluxDB v2 server and the
InfluxDB v2 Source all authenticate with the same token. Assign that group to this
deployment (or your project/environment); the datasource reads **INFLUXDB2_TOKEN** from it.
The legacy `INFLUXDB_TOKEN` variable still works for deployments created before the group
was introduced.

Note that `provisioning/datasources/influxdb.yaml` still hard-codes the datasource URL
(`http://influxdb:80`), organization and database, which match the group defaults. Edit
that file if your InfluxDB is elsewhere.

## How to Run

1. Log in or sign up at [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Set `GF_SECURITY_ADMIN_PASSWORD`, and assign the `influxdb2-config` variable group so the InfluxDB datasource gets its token.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## Save dashboards with code

Dashboards can be [exported](https://grafana.com/docs/grafana/latest/dashboards/share-dashboards-panels/#export-a-dashboard-as-json) and saved under the `provisioning` folder, see `sensors.json` for example. This allows you to programmatically set up dashboards and protected them from accidental modification or if you want to set them up in other environments.

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Grafana and is offered as-is, with no Grafana specific support from Quix.