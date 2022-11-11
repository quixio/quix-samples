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
Create an account on [Quix](https://portal.platform.quix.ai/self-sign-up?xlink=github) to edit or deploy this application as a service. A public URL for the API will be provisioned by Quix for you when you deploy the app.