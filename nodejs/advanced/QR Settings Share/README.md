# QR Settings Share

Share settings to external apps with a QR code.

## Docs

Check out the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.

## How to run

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application without a local environment setup.

NOTE! Whether running locally or in the Quix platform you should edit `environment-variables.service.ts` and add your Token.
This can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)
![image](/src/assets/images/small-menu.png)

## Local

You will need to run both the UI and API.

You can run the API in Quix or locally as long as the UI has access to it. 

### UI

To run this project locally please update the `quix.service.ts` file with your:
 - Workspace ID - The id of your Quix workspace. See the URL in your browser when you're logged in
 - Token - A secure token used by apps and websites to access Quix data

The Token can be obtained from the Quix portal under the Token menu item (top right of the page under your user avatar)
![image](small-menu.png)

In the UI folder:
Run `npm install --force` to install all the dependencies
Run `ng serve` to build and run the . Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

NOTE! You may need to amend the URL for accessing the API when running locally.
This can be found in the `quix.service.ts` file.

### API

To run the API locally ensure you have `node` installed.

In the API folder:
Run `node main.js`