# Sentiment demo UI

This is an example of how to use Quix with NodeJs.

 - It implements a system of chat rooms where people can communicate. 
 - QR codes are used to invite new participants into the chat room.
 - Sentiment of the chat is analyzed in another service and displayed here.

## Environment variables

This code sample uses the following environment variables:

- **messages**: This is the output topic for chat messages
- **sentiment**: This is the input topic for sentiment score from ML model. Use Hugging Face model library item to analyze messages sentiment.

## Connection
This app integrates with Quix via Quix WebSocket gateway. For more please refer to [Quix docs](https://documentation.platform.quix.ai/apis/streaming-reader-api/intro.html).

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

NOTE! Whether running locally or in the Quix platform you should edit `environment-variables.service.ts` and add your Token.
This can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)

### Debug In Quix

If you wan to debug your javascript / typescript with the code deployed in the Quix serverless environment, please edit the docker file in the build folder.

The following line runs the build
`RUN npm run build -- --output-path=./dist/out --configuration production`

Remove ` --configuration production` to skip minification and other production ready steps.

The scripts will now be visible in your browsers debugger. The sources tab will now show webpack:// files.

## Local

To run this project locally please update the `quix.service.ts` file with your:
 - Topics (messages and sentiment) - note that you need to get the Topic ID from the Topic page for this.

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.
