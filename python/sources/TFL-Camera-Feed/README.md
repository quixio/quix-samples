# TFL Camera Feed

Stream TFL's London traffic camera images to Quix

## Requirements/prerequisites (optional)
	
You need a [TFL (Transport For London)](https://api-portal.tfl.gov.uk/) account and the API keys to use this service:
- Register for an account.
- Login and click the "Products" menu item.
- You should have 1 product to choose from "500 Requests per min."
- Click "500 Requests per min."
- Enter a name for your subscription into the box, e.g. QuixFeed, and click "Register."
- You can now find your API Keys in the profile page.

## Environment variables

This code sample uses the following environment variables:

- **output**: This is the output topic for TFL camera images
- **frame_rate**: The frame rate you want to use
- **api_key**: Your TFL API Key

## Docs
{This will contain any available references and links to documentation or resource related to the code.}

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

Alternatively, you can visit [here](https://quix.ai/docs/sdk/python-setup.html) to learn how to setup your local environment.