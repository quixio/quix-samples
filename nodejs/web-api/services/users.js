const express = require('express')
const { randomUUID } = require('crypto')

const users = [
    {
        'id': randomUUID(),
        'name': "John Doe"
    },
    {
        'id': randomUUID(),
        'name': "Jane Doe"
    }
]

const getAll = () => users

module.exports = {
    getAll
}