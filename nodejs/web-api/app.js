const express = require("express")
const cors = require("cors")
const helmet = require("helmet")
const { unless } = require("express-unless")
const swaggerUi = require("swagger-ui-express")
const { expressjwt: jwt } = require("express-jwt")

const users = require("./routes/users")
const { logger: log } = require("./utils/logger")
const swaggerDocument = require("./swagger.json")

const app = express()
const port = 80

// enable cross-origin request sharing
app.use(cors())

// enable jwt token authentication
if (process.env.JWT_AUTH_SECRET) {
    const jwtOpts = { secret: process.env.JWT_AUTH_SECRET }
    if (process.env.JWT_AUTH_ALGORITHM) {
        jwtOpts["algorithms"] = [process.env.JWT_AUTH_ALGORITHM]
    }
    if (process.env.JWT_AUTH_AUDIENCE) {
        jwtOpts["audience"] = [process.env.JWT_AUTH_AUDIENCE]
    }
    if (process.env.JWT_AUTH_ISSUER) {
        jwtOpts["issuer"] = [process.env.JWT_AUTH_ISSUER]
    }
    app.use(helmet())
    app.use(jwt(jwtOpts).unless({ path: [/^\/swagger/] }))
    log.info("JWT token auth enabled")
} else {
    log.warn("JWT token auth disabled")
}

// enable swagger docs for your API
if (process.env.SWAGGER_ENABLE.toLowerCase() == "true") {
    var options = {}
    if (process.env.JWT_AUTH_SECRET) {
        swaggerDocument.components.securitySchemes = {
            bearer: {
                type: "http",
                scheme: "bearer"
            }
        }
        swaggerDocument.security = [{bearer: []}]
    }
    app.use("/swagger", function(req, res, next) {
        swaggerDocument.host = req.get("host");
        req.swaggerDoc = swaggerDocument;
        next();
    }, swaggerUi.serveFiles(swaggerDocument, options), swaggerUi.setup())
    log.info("Swagger docs for API is available at /swagger")
}

// register your routes
app.use("/users", users)

app.listen(port, () => console.log(`Server listening on port ${port}`))

module.exports = app