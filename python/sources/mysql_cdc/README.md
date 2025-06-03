# MySQL CDC

This connector demonstrates how to capture changes to a MySQL database table (using CDC) and publish the change events to a Kafka topic using MySQL binary log replication.

## How to run

1. Set up your MySQL database with binary logging enabled
2. Configure environment variables for MySQL connection
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Environment variables

The connector uses the following environment variables:

- **output**: Name of the output topic to write into.
- **MYSQL_HOST**: The IP address or fully qualified domain name of your MySQL server.
- **MYSQL_PORT**: The Port number to use for communication with the server (default: 3306).
- **MYSQL_DATABASE**: The name of the database for CDC.
- **MYSQL_USER**: The username that should be used to interact with the database.
- **MYSQL_PASSWORD**: The password for the user configured above.
- **MYSQL_SCHEMA**: The name of the schema/database for CDC (same as MYSQL_DATABASE).
- **MYSQL_TABLE**: The name of the table for CDC.

## Requirements / Prerequisites

- A MySQL Database with binary logging enabled.
- Set `log-bin=mysql-bin` and `binlog-format=ROW` in MySQL configuration.
- MySQL user with `REPLICATION SLAVE` and `REPLICATION CLIENT` privileges.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.