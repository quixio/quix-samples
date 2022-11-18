import express, { Request, Response, NextFunction } from "express";
import cors from "cors";
import helmet from "helmet";
import { unless } from "express-unless";
import swaggerUi from "swagger-ui-express";
import { expressjwt as jwt } from "express-jwt";

import userRoutes from "./routes/user.route";
import { logger } from "./utils/logger";

const swaggerDocument: any = require("../swagger.json");

const app = express();
const port: number = 80;

app.set('trust proxy', true);

// enable cross-origin request sharing
app.use(cors())

// enable jwt token authentication
if (process.env.JWT_AUTH_SECRET) {
    const jwtOpts: any = { secret: process.env.JWT_AUTH_SECRET };
    if (process.env.JWT_AUTH_ALGORITHM) {
        jwtOpts.algorithms = [process.env.JWT_AUTH_ALGORITHM];
    }
    if (process.env.JWT_AUTH_AUDIENCE) {
        jwtOpts.audience = [process.env.JWT_AUTH_AUDIENCE];
    }
    if (process.env.JWT_AUTH_ISSUER) {
        jwtOpts.issuer = [process.env.JWT_AUTH_ISSUER];
    }

    app.use(helmet());
    app.use(jwt(jwtOpts).unless({ path: [/^\/swagger/] }));

    // custom error handler
    app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
        if (err.name === "UnauthorizedError") {
            logger.info(`Failed authentication: ${err.message} (${req.ip})`);
            res.statusMessage = "Unauthorized";
            res.status(401).end();
        } else {
            next(err);
        }
    });

    logger.info("JWT token auth enabled");
} else {
    logger.warn("JWT token auth disabled");
}

// enable swagger docs for your API
if (process.env.SWAGGER_ENABLE?.toLowerCase() === "true") {
    if (process.env.JWT_AUTH_SECRET) {
        swaggerDocument.components.securitySchemes = {
            bearer: {
                type: "http",
                scheme: "bearer"
            }
        };
        swaggerDocument.security = [{ bearer: [] }];
    }
    app.use("/swagger", (req: Request, res: Response, next: NextFunction) => {
            swaggerDocument.host = req.get("host");
            next();
        }, swaggerUi.serveFiles(swaggerDocument, {}), swaggerUi.setup());
    logger.info("Swagger docs for API is available at /swagger");
}

// register your routes
app.use("/users", userRoutes);

app.listen(port, () => console.log(`Server listening on port ${port}`));