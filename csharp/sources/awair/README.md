# Awair importer
This sample will connect to Awair's background services to continously scrape and publish data for your devices.

## Requirements

You will need to register for a [developer account](https://developer.getawair.com/onboard/welcome) to access your Awair data. Once you have that, you can get your access token from [here](https://developer.getawair.com/console/access-token).

## Environment variables

The code sample uses the following environment variables:

- **Topic**: This is the ouput topic where data will be written to.
- **Awair__Token**: The token needed to communicate with Awair API.

## Limitations
Due to the rate limit of the Awair endpoints, data will only be scraped when the application starts then every 5 minutes afterwards for the elapsed period.

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to run
This bridge can run locally or in our serverless environment. To learn how to deploy services in Quix, please create an account at [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) and see our [docs](https://quix.ai/docs/guides/index.html).

