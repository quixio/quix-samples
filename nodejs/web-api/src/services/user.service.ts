import { randomUUID } from "crypto";
import { User } from "../models/user";

const users: User[] = [
    {
        'id': randomUUID(),
        'name': "John Doe"
    },
    {
        'id': randomUUID(),
        'name': "Jane Doe"
    }
];

const getAll = () => users;

export = {
    getAll
};