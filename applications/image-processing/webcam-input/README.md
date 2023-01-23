# Webcam image capture

Stream images from the webcam on your laptop or phone to a Quix stream.

## Environment variables

This code sample uses the following environment variables:

- **webcam_output**: This output topic will contain images from the webcam

## How to run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

## Local setup

Clone the repo or download a zip of the source.

Update the `quix.service.ts` file with your values for these:

 - private workingLocally = false; // set to true if working locally
 - private token: string = ""; // From the Topics page, copy an SDK token from the broker settings
 - public workspaceId: string = ''; // Look in the URL for the Quix Portal your workspace ID is after 'workspace='
 - public topic: string = ''; // get topic name from the Topics page in Quix portal

Ensure you have npm installed locally.

Run `npm install`
And `ng serve`


 