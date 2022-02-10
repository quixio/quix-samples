# Strava bridge
Strava is a popular social-fitness network that enables its users to track and share their exercise activities. You can stream your fitness data from Strava to Quix seamlessly as the data is synced from your fitness devices to Strava.

This service allows you to periodically import data from your Strava account.

## Requirements / Prerequisites

Find out how to obtain the required Strava tokens [here](http://developers.strava.com/docs/getting-started/)

## Environment Variables

The code sample uses the following environment variables:

- **output**: This is the output topic for Strava data
- **PATToken**: Your Quix Personal Access Token
- **ClientId**: This is the Strava Client ID
- **ClientSecret**: The Strava Client Secret
- **StravaRefreshToken**: The Strava Refresh Token

## Why connect your Strava to Quix?

Strava allows you to keep track of and manage your fitness activities. With Quix you can build a distributed network of computational models to perform complex analytics on your data. Quix will allow you to experience the power of your fitness data in its full force.

In this example, we are going to build and deploy a service that injests data from Strava to Quix streams continously. This guide assumes that you already have a Strava account and Quix workspace. Otherwise, you can create a Strava account at [Strava](https://www.strava.com/) and sign up for a Quix account at [Quix.ai](https://quix.ai).

## Regsiter an API application on Strava

To find out how to authorize Quix to make use of your Strava data, please follow our guide [here](https://github.com/quixai/strava-bridge/edit/main/README.md#register-an-api-application-on-strava)

## Docs

Check out the [SDK Docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance

## How to Run
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to Edit or Deploy this application without a local environment setup.
