const winston = require('winston');

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL ? process.env.LOG_LEVEL : 'info',
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
  ],
})

module.exports = {
    logger
}