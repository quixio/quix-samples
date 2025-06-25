# Prometheus Pushgateway

This sample demonstrates how to deploy and use the Prometheus Pushgateway in your monitoring pipeline. Please note: this image is provided by Prometheus and is offered as-is, with no specific support from Quix.

## How to Run

1. Log in or sign up at [Quix](https://portal.platform.quix.io/signup?xlink=github) and navigate to the Code Samples section.
2. Click **Deploy** to launch a pre-built container.
3. Fill in the required environment variables for your Prometheus Pushgateway instance.
4. Ensure container state is enabled; otherwise, any pushed metrics or configuration may be lost on restart.

## Pushing Metrics

The Prometheus Pushgateway is designed to accept metrics from ephemeral or batch jobs. For guidance on pushing metrics, refer to the [Prometheus documentation](https://prometheus.io/docs/practices/pushing/).

## Contribute

Feel free to fork this project on the [GitHub](https://github.com/quixio/quix-samples) repository and contribute your enhancements. Any accepted contributions will be attributed accordingly.

## License & Support

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo. Remember, this image is provided by Prometheus and is offered as-is, with no Prometheus specific support from Quix.
