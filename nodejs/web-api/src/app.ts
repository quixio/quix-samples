import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import helmet from "helmet";
import { unless } from "express-unless";
import swaggerUi from "swagger-ui-express";
import { expressjwt as jwt } from "express-jwt";
import jwksRsa from "jwks-rsa";

import userRoutes from "./routes/user.route";
import { logger } from "./utils/logger";

const swaggerDocument: any = require("../swagger.json");

const app = express();
const authEnabled = process.env.JWT_AUTH_ISSUER;
// must be set to port 80 when deploying to Quix. 
const port = process.env.PORT ? +process.env.PORT : 80;

app.set('trust proxy', true);

// enable cross-origin request sharing
app.use(cors());
app.use(express.json());

if (authEnabled) {
    // enable jwt token authentication
    const jwtOpts: any = {};
    if (process.env.JWT_AUTH_ISSUER)
        jwtOpts.issuer = [process.env.JWT_AUTH_ISSUER];
    if (process.env.JWT_AUTH_SECRET)
        jwtOpts.secret = process.env.JWT_AUTH_SECRET;
    else {
        jwtOpts.secret = jwksRsa.expressJwtSecret({
            cache: true,
            rateLimit: true,
            jwksRequestsPerMinute: 5,
            jwksUri: `${jwtOpts.issuer}.well-known/jwks.json`
        });
    }
    if (process.env.JWT_AUTH_ALGORITHM)
        jwtOpts.algorithms = [process.env.JWT_AUTH_ALGORITHM];
    if (process.env.JWT_AUTH_AUDIENCE)
        jwtOpts.audience = [process.env.JWT_AUTH_AUDIENCE];

    app.use(helmet());
    app.use(jwt(jwtOpts).unless({ path: [/^\/swagger/, /^\/api-docs/] }));
    app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
        // custom error handler
        if (err.name === "UnauthorizedError") {
            logger.info(`Authentication failed: ${err.message} (${req.ip})`);
            res.statusMessage = "Unauthorized";
            res.status(401).end();
        } else {
            next(err);
        }
    });
    logger.info("JWT auth enabled");
} else {
    logger.warn("JWT auth disabled");
}

if (process.env.SWAGGER?.toLowerCase() === "true") {
    // enable swagger docs for your API
    if (authEnabled) {
        swaggerDocument.components.securitySchemes = {
            bearer: {
                type: "http",
                scheme: "bearer"
            }
        };
        swaggerDocument.security = [{ bearer: [] }];
    }

    var options = {
        swaggerOptions: {
            url: "/api-docs/swagger.json",
        },
    };

    app.get("/api-docs/swagger.json", (req, res) => res.json(swaggerDocument));
    app.use("/swagger", (req: Request, res: Response, next: NextFunction) => {
        swaggerDocument.host = req.get("host");
        next();
    }, swaggerUi.serveFiles(undefined, options), swaggerUi.setup(undefined, options));
    logger.info("Swagger docs for API is available at /swagger");
}

// register your routes
app.use("/users", userRoutes);

app.listen(port, () => console.log(`Server listening on port ${port}`));