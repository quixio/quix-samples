# Segment Webhook

Stream Segment event data into Quix with this webhook implementation.

It's secure, using a secret shared with both Quix and Segment.

And we've used Waitress “… a production-quality pure-Python WSGI server with very acceptable performance. It has no dependencies except ones that live in the Python standard library. It runs on CPython on Unix and Windows.”

## Requirements/prerequisites (optional)

A [Segment](https://app.segment.com/) account.

## Environment variables

This code sample uses the following environment variables:

- **output**: The output topic to stream Segment data into
- **shared_secret**: The secret you configured in Segment

## Docs
Check out the [SDK docs](https://docs.quix.io/sdk-intro.html) for detailed usage guidance.

## How to run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

Alternativelly, you can visit [here](https://docs.quix.io/sdk/python-setup.html) to learn how to setup your local environment.