# TFL image processing UI

A UI showing the image feed and a map of vehicle counts.

## Environment variables

This code sample uses the following environment variables:

- **processed**: The input topic for the UI. Containing images and vehicle counts.

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

NOTE! Whether running locally or in the Quix platform you should edit `environment-variables.service.ts` and add your Token.
This can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)
![image](/src/assets/images/small-menu.png)

## Local

To run this project locally please update the `environment-variables.service.ts` file with your:
 - Topic (the topic you want to receive data from)
 - Workspace ID (the id of your Quix workspace. See the URL in your browser when you're logged in)

Set the `UseHardcodedValues` flag to True

NOTE! Whether running locally or in the Quix platform you should edit `environment-variables.service.ts` and add your Token.
This can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)
![image](/src/assets/images/small-menu.png)

Optionally, to move into production you should uncomment the script tag in `index.html` and add your Google Maps API key   

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.
