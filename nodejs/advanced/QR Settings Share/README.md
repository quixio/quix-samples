# QR Settings Share

[This project](https://github.com/quixio/quix-library/tree/main/nodejs/advanced/QR%20Settings%20Share){target="_blank"} enables sharing of tokens and other app settings with the [Quix Tracker](https://github.com/quixio/quix-tracker) app via a QR code.

## How to run

Create a [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) account or log-in and visit the Library to use this project.

Clicking `Setup & deploy` on the library item, deploys a pre-built container in Quix. Complete the environment variables to configure the container.

Clicking `Edit code` on the library item, forks the project to your own Git repo so you can customize it before deploying.

NOTE! If running locally you should read the `Local` section below.

### Tokens

A quick note on PAT or Personal Access Tokens.

The PAT token used by default will expire. It is recommended that you generate a new token and update the `quix.service.ts` file. 

## Local

You will need to run both the UI and API portions of this project separately.

You can run the API in Quix or locally as long as the UI has access to it. 

### UI

To run this project locally:

1. update the `quix.service.ts` file with your:
   - Workspace ID - The id of your Quix workspace. See the URL in your browser when you're logged in
   - Token - A secure token used by apps and websites to access Quix data
   - Set `workingLocally` to `true`

2. The Token can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)

3. In the UI folder:
Run `npm install --force` to install all the dependencies
Run `ng serve` to build and run the . Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

NOTE! You may need to amend the URL for accessing the API when running locally.
This can be found in the `quix.service.ts` file.

### API

To run the API locally ensure you have `node` installed.

In the API folder:
Run `node main.js`

## Debug In Quix

If you want to debug your javascript / typescript with the code deployed in the Quix serverless environment, please edit the docker file in the build folder.

The following line runs the build
`RUN npm run build -- --output-path=./dist/out --configuration production`

Remove ` --configuration production` to skip minification and other production ready steps.

The scripts will now be visible in your browsers debugger. The sources tab will now show `webpack://` files.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-library){target="_blank"} repo.

Please star us and mention us on social to show your appreciation.


