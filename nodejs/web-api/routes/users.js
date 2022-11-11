const express = require('express')
const users = require('../controllers/users')

const router = express.Router()

router.get('/', users.getAll)

module.exports = router