import express from "express";
import users from "../controllers/user.controller";

const userRouter = express.Router();

userRouter.get('/', users.getAll);

export = userRouter;