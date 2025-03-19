# Grafana

This sample demonstrates how to deploy and use Grafana as a visualization tool in your Quix Cloud pipeline. Please note: this image is provided by Grafana and is offered as-is, with no specific support from Quix.

## How to Run

1. Log in or sign up at [Quix](https://portal.platform.quix.io/signup?xlink=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Fill in the required environment variables for your Grafana instance.
4. Enable state, otherwise changes will be lost on restart. Please note, the necessary storage type may not be supported on all Quix Platforms.

## Save dashboards with code

Dashboards can be [exported](https://grafana.com/docs/grafana/latest/dashboards/share-dashboards-panels/#export-a-dashboard-as-json) and saved under the `provisioning` folder, see `sensors.json` for example. This allows you to programmatically set up dashboards and protected them from accidental modification or if you want to set them up in other environments.

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Grafana and is offered as-is, with no Grafana specific support from Quix.