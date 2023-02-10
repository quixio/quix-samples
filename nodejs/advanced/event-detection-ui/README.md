# Event Detection Demo UI

This is the UI for the event detection demo. Stream data from your phone or a data generator and see the telemetry in this UI in real-time. Run an event detection service and you can also see event time and location too.

## Docs

Check out the [API docs](https://docs.quix.io/apis/streaming-reader-api/intro/) for detailed API usage guidance and how to connect to the WebSockets API using SignalR.

## How to run in the Quix Portal

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

## Local development

To run this project locally please update the following values in `environment-variables.service.ts`:

``` 
  private workingLocally = false; // set to true if working locally
  public token: string = ''; // Create a token in the Tokens menu and paste it here
  public topic: string = ''; // Create a topic in the Topic tab - for this demo use `demo-data`
  public eventTopic: string = ''; // Create a topic in the Topic tab - for this demo use `events`
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after `workspace=`
```
  
The Token can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)

Run `npm install --force` to install all the dependencies
Run `ng serve` to build and run the . Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.
