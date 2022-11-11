const express = require('express')
const users = require('../services/users')

const getAll = async (req, res) => res.json(users.getAll())

module.exports = {
    getAll
}