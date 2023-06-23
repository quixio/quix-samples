# Image processing UI

[This project](https://github.com/quixio/quix-samples/tree/main/nodejs/advanced/Image-Processing-UI) is a companion user interface (UI) to the other TfL projects. It shows the image feed from TfL traffic cameras and a map with the count of each object detected using a YOLO V3 model.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Samples to use this project.

Clicking `Deploy` on the Sample, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the Sample, forks the project to your own Git repo so you can customize it before deploying.

NOTE! If running locally you should read the `Local` section below.

## Environment variables

This code sample uses the following environment variables:

- **processed**: The input topic for the UI. Containing images and vehicle counts.

## Local

To run this project locally please update the `quix.service.ts` file with your:
 - Topic (the topic you want to receive data from)
 - Workspace ID (the id of your Quix workspace. See the URL in your browser when you're logged in)
 - Token (This can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)

Set the `UseHardcodedValues` flag to True

Optionally. To move into production, you should uncomment the script tag in `index.html` and add your Google Maps API key. This will remove the `Development use only` watermark.   

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

### Debug In Quix

If you want to debug your javascript / typescript with the code deployed in the Quix serverless environment, please edit the docker file in the build folder.

The following line runs the build
`RUN npm run build -- --output-path=./dist/out --configuration production`

Remove ` --configuration production` to skip minification and other production ready steps.

The scripts will now be visible in your browsers debugger. The sources tab will now show `webpack://` files.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.

