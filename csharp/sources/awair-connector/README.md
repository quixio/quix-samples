# Awair

[This project](https://github.com/quixio/quix-samples/tree/main/csharp/sources/awair-connector) will connect to Awair's background services to continuously scrape and publish data for your devices.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Environment variables

The code sample uses the following environment variables:

- **Topic**: This is the output topic where data will be written to.
- **Awair__Token**: The token needed to communicate with Awair API.

## Requirements

You will need to register for a [developer account](https://developer.getawair.com/onboard/welcome) to access your Awair data. Once you have that, you can get your access token from [here](https://developer.getawair.com/console/access-token).

## Limitations

Due to the rate limit of the Awair endpoints, data will only be scraped when the application starts then every 5 minutes afterwards for the elapsed period.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

