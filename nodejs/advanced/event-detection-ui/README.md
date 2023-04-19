# Event Detection Demo UI

[This project](https://github.com/quixio/quix-samples/tree/main/nodejs/advanced/event-detection-ui) 
is the UI for our event detection demo. 

Stream data from your phone or a data generator and view the telemetry in this UI in real-time. Deploy an event detection service and you can also see the events time and location.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Setup & deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Local development

To run this project locally update the following values in `environment-variables.service.ts`:

``` 
  private workingLocally = false; // set to true if working locally
  public token: string = ''; // Create a token in the Tokens menu and paste it here
  public topic: string = ''; // Create a topic in the Topic tab - for this demo use `demo-data`
  public eventTopic: string = ''; // Create a topic in the Topic tab - for this demo use `events`
  public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after `workspace=`
```
  
The Token can be obtained from the Quix portal under the `Token` menu (top right of the page under your user avatar)

Then install dependencies:

```
Run `npm install --force` to install all the dependencies
```

And finally, run the solution:

```
Run `ng serve` to build and run the . Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.
```

## Docs

This UI makes use of the Streaming Reader API. Check out the [API docs](https://docs.quix.io/apis/streaming-reader-api/intro/) for detailed API usage guidance and how to connect to the WebSockets API using SignalR.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

