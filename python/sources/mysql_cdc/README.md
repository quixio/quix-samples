# MySQL CDC

[This connector](https://github.com/quixio/quix-samples/tree/main/python/sources/mysql_cdc) streams row-level changes from one MySQL table to a Kafka topic by reading the server's binary log. It is built on the Quix Streams [`MySqlCdcLiteSource`](https://github.com/quixio/quix-streams/blob/v3.27.0/docs/connectors/sources/mysql-cdc-lite-source.md), a Community connector.

## How to run

Create a [Quix](https://portal.cloud.quix.io/signup?utm_campaign=github) account or log-in and visit the `Connectors` tab to use this connector.

Clicking `Set up connector` allows you to enter your connection details and runtime parameters.

Then either:
* click `Test connection & deploy` to deploy the pre-built and configured container into Quix.

* or click `Customise connector` to inspect or alter the code before deployment.

## Before you deploy

The connector checks only the first item below; check the rest yourself. Run the checks as an admin user on the MySQL server the connector replicates from.

- **`binlog_format` is `ROW`.** Checked at start-up: the connector refuses to start otherwise.
  ```sql
  SHOW GLOBAL VARIABLES LIKE 'binlog_format';
  ```
- **`binlog_row_metadata` is `FULL`.** MySQL 8 ships `MINIMAL`, which gives `UNKNOWN_COL0..n` column names, and silently wrong values for unsigned columns and `null` for `SET`/`ENUM`.
  ```sql
  SHOW GLOBAL VARIABLES LIKE 'binlog_row_metadata';
  ```
- **`binlog_row_image` is `FULL`.** It has session scope, so check it on each writer's connection too.
  ```sql
  SHOW GLOBAL VARIABLES LIKE 'binlog_row_image';
  SELECT @@session.binlog_row_image;
  ```
- **The grants.** Exactly this set is enough:
  ```sql
  GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc'@'%';
  GRANT SELECT ON mydb.mytable TO 'cdc'@'%';
  ```
  Check them with `SHOW GRANTS FOR 'cdc'@'%';`.
- **`binlog_expire_logs_seconds` outlasts your longest downtime.** Check `SHOW BINARY LOGS;` as well, because MySQL 8.4's `binlog_space_limit` can purge files earlier.
  ```sql
  SHOW GLOBAL VARIABLES LIKE 'binlog_expire_logs_seconds';
  SHOW BINARY LOGS;
  ```
- **`binlog_transaction_compression` is `OFF`.** Compressed transactions are dropped silently.
  ```sql
  SHOW GLOBAL VARIABLES LIKE 'binlog_transaction_compression';
  ```
- **`binlog_row_value_options` is empty.** `PARTIAL_JSON` updates are dropped silently.
  ```sql
  SHOW GLOBAL VARIABLES LIKE 'binlog_row_value_options';
  ```
- **Exactly one replica.** The replication client id is derived from the source name, database and table, so replicas evict each other. Two deployments against the same table need different `MYSQL_SOURCE_NAME` values.

What each misconfiguration looks like downstream is in the [full checklist](https://github.com/quixio/quix-streams/blob/v3.27.0/docs/connectors/sources/mysql-cdc-lite-source.md#before-you-deploy-the-checklist).

## Environment variables

The connector uses the following environment variables:

- **output**: Kafka topic that receives one message per changed row, keyed `<database>.<table>`.
- **MYSQL_HOST**: Hostname or IP address of the MySQL server to replicate from.
- **MYSQL_PORT**: MySQL server port.
- **MYSQL_USER**: MySQL user with REPLICATION SLAVE and REPLICATION CLIENT on *.* and SELECT on the table.
- **MYSQL_PASSWORD**: Password of MYSQL_USER.
- **MYSQL_DATABASE**: Database (schema) that contains the table.
- **MYSQL_TABLE**: Table to capture changes from.
- **MYSQL_TLS**: `true` encrypts without verifying the server certificate; a CA file path (e.g. `/etc/ssl/certs/ca-certificates.crt`) encrypts and verifies the certificate and hostname; `false` connects in plaintext.
- **MYSQL_COMMIT_INTERVAL**: Seconds between producing buffered changes and committing the binlog position; bounds the delay between a change and its message.
- **MYSQL_SOURCE_NAME**: Leave empty for `mysql_cdc_lite_<database>_<table>`. Sets the state store and replication client id: changing it restarts from the server's current binlog position. Change it only to re-seed after a purged position or to avoid a server_id collision.

## Message format

The message key is the string `"<database>.<table>"`.

The message value is a JSON object with a fixed envelope:

```json
{
  "kind": "update",
  "schema": "mydb",
  "table": "mytable",
  "columnnames": ["id", "customer", "amount"],
  "columnvalues": [1, "ada", 250],
  "oldkeys": {
    "keynames": ["id", "customer", "amount"],
    "keyvalues": [1, "ada", 100]
  }
}
```

- `kind` is `"insert"`, `"update"` or `"delete"`.
- `columnnames`/`columnvalues` carry the row *after* the change. They are empty lists for a `"delete"`.
- `oldkeys` carries the row *before* the change, as `keynames`/`keyvalues`. It is `{}` for an `"insert"`.

How each MySQL column type is encoded is in the [type-encoding table](https://github.com/quixio/quix-streams/blob/v3.27.0/docs/connectors/sources/mysql-cdc-lite-source.md#message-data-formatschema).

## Things to know

- **No initial snapshot.** Rows already in the table are never published; the topic starts at the binlog position of the first start.
- **At-least-once.** A crash between producing and committing replays the last batch. Deduplicate on the primary key inside `columnvalues`/`oldkeys` plus `kind`.
- **Restart resumes** from the committed position, so changes made while the connector was stopped arrive when it starts again.
- **Changing `MYSQL_SOURCE_NAME` resets that position.** The connector then starts from the server's current position. The purged-position error names this as the re-seed step.
- **The default `MYSQL_TLS=true` does not authenticate the server.** It encrypts, but checks no certificate and no hostname. Set `MYSQL_TLS` to a CA file path to verify them.
- **One table goes to one partition.** Every message has the same key, so extra partitions on `output` add nothing.

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.
