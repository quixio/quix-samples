# Webcam image capture

[This project](https://github.com/quixio/quix-samples/tree/main/applications/image-processing/webcam-input) allows you to stream images from the webcam on your laptop or phone to a Quix stream.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Setup & deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

## Local setup

 - Ensure you have npm installed locally

 - Clone the repo or download a zip of the source

 - Update the `quix.service.ts` file with your values for these:

   - private workingLocally = false; // set to true if working locally
   - private token: string = ""; // From the Topics page, copy an QuixStreams/SDK token from the broker settings
   - public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
   - public topic: string = ''; // get topic name from the Topics page in Quix portal

 - Run `npm install`
 - Run `ng serve`

## Environment variables

This code sample uses the following environment variables:

- **webcam_output**: Images from the webcam will be streamed to this topic

Pass them at run-time when working locally or configure them in the Quix portal.

## Details

This app uses the Quix [TelemetryWriter](https://docs.quix.io/apis/streaming-writer-api/intro.html) to stream images to a topic.

Have a look at the `quix.service.ts` file to see how it's done.

The data packets streamed to Quix contain the timestamp in milliseconds, the image as a base64 string and the latitude and longitude of the device.

```
{
    Timestamps: [new Date().getTime() * 1000000],
    StringValues: {"image": [webcamImage.imageAsBase64]},
    NumericValues: {"lat": [this.lat], "lon": [this.long]}
}
```

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

