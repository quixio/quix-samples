import { Request, Response } from "express";
import users from "../services/user.service";

const getAll = async (req: Request, res: Response) => res.json(users.getAll());

export = {
    getAll
};