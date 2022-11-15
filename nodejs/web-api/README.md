# NodeJs Web API Template

This is an empty template for a web API using Node.js and Express in the Quix serverless environment.

## Environment variables

This code sample uses the following environment variables:

- **JWT_AUTH_ISSUER**: Jason web token issuer (optional, but recommended).
- **JWT_AUTH_AUDIENCE**: Jason web token audience (optional, but recommended).
- **JWT_AUTH_SECRET**: Jason web token signing key secret (for symmetric-key signing) or public key or asymmetric-key signing (required to enable JWT authentication).
- **JWT_AUTH_ALGORITHM**: Jason web token signing algorithm (required).
- **SWAGGER_ENABLE**: Set to 'true' enable Swagger for the API. API documentation must be added to swagger.json file in the root directory (optional).
- **LOG_LEVEL**: Minimum log level (optional).
 
## Docs

For documentation related to JWT authentication, refer to [express-jwt](https://github.com/auth0/express-jwt).
For documentation related to Swagger UI, refer to [swagger-ui-express](https://github.com/scottie1984/swagger-ui-express).
For documentation related to logging, refer to [winston](https://github.com/winstonjs/winston).

## How to run

### On Quix Platform

Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application as a service. A public URL for the API will be provisioned by Quix for you when you deploy the app.

### On a local environment

To run the web api on your local machine, you need to have NodeJs and npm (comes with NodeJs) installed on your machine. You can find the installers for different platforms below.
 
 - Windows: [NodeJs download](https://nodejs.org/en/download/)
 - macOS: [NodeJs download](https://nodejs.org/en/download/)
 - Linux: download from the package repository of your Linux distribution (recommended) or install from [source](https://nodejs.org/en/download/).

Note that if you need to work with multiple versions of NodeJS (especially on platforms that only allows installing one version of NodeJS such as rolling release Linux distributions), it is recommended to use [nvm](https://github.com/nvm-sh/nvm) when installing NodeJs.

Run the following commands on your terminal (e.g. PowerShell on Windows or teminal emulators on macOS or Linux).

1. Verify that you have both NodeJs and npm installed:

```
# below commands should display the versions of NodeJs and npm if they are installed.
node --version
npm --version
```

2. Clone the project from Quix (recommendedn, requires [git](https://git-scm.com/)) or download the project as a zip file and extract it.

3. Navigate to the project folder:

```
cd /path/to/project
```

4. Set the environmental variables listed in [environmental variables](#environment-variables).[^1]

5. Install dependencies:

```
npm install
```

6. Build the project[^2]:

```
npm run build
```

7. Start the API:
```
npm start
```

[^1]: Steps for setting environmental variables depend on the programming environment you are using. If you are using an IDE, please consult the documentation for your IDE on how to set environmental variables. Otherwise, consult documentation for your OS for guidance for setting environmental variables.

[^2]: The listening port of the web service is hard-coded in the _app.ts_ file to 80. Ths is because Quix sets up port forwarding and configures DNS for public access automatically when running the API on Quix, and hence, is not meant to be modified. However, if you are debugging the service locally, you may want to change this to a port number greater than 1024 (e.g. 8080) as Unix-based systems may require privileged access to listen on port numbers less than 1024.