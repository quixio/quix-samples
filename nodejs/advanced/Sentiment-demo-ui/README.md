# Chat app

This is an example of how to use Quix with JavaScript.

It implements a system of chat rooms where people can have communicate. It use QR codes to invite new participants into the chat room. 

## Environment variables

This code sample uses the following environment variables:

- **messages**: This is the output topic for chat messages
- **sentiment**: This is the input topic for sentiment score from ML model. Use Hugging Face model library item to analyze messages sentiment.

## Connection
Chat app integrates with Quix via Quix WebSocket gateway. For more please refer to [Quix docs](https://documentation.platform.quix.ai/apis/streaming-reader-api/intro.html).

## Set up
This project was generated with [Angular CLI](https://github.com/angular/angular-cli) version 9.1.3.

### Development server

Run `ng serve` for a dev server. Navigate to `http://localhost:4200/`. The app will automatically reload if you change any of the source files.

### Code scaffolding

Run `ng generate component component-name` to generate a new component. You can also use `ng generate directive|pipe|service|class|guard|interface|enum|module`.

### Build

Run `ng build` to build the project. The build artifacts will be stored in the `dist/` directory. Use the `--prod` flag for a production build.

### Running unit tests

Run `ng test` to execute the unit tests via [Karma](https://karma-runner.github.io).

### Running end-to-end tests

Run `ng e2e` to execute the end-to-end tests via [Protractor](http://www.protractortest.org/).

### Further help

To get more help on the Angular CLI use `ng help` or go check out the [Angular CLI README](https://github.com/angular/angular-cli/blob/master/README.md).

## Docs

Visit the [SDK docs](https://quix.ai/docs/sdk/introduction.html) for detailed usage guidance.