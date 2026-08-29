# MySQL CDC

This connector demonstrates how to capture changes to a MySQL database table (using CDC) and publish the change events to a Kafka topic using MySQL binary log replication. It's built using **Quix Streams StatefulSource** to ensure exactly-once processing and automatic recovery after restarts.

## Key Features

- **Quix Streams StatefulSource**: Built on Quix Streams' robust stateful source framework
- **Automatic State Management**: Integrated state store for binlog position and snapshot tracking
- **Exactly-Once Processing**: No data loss during application restarts or failures
- **Initial Snapshot**: Optionally capture existing data before starting CDC
- **Automatic Recovery**: Seamlessly resume processing after interruptions
- **Change Buffering**: Batches changes for efficient Kafka publishing

## How to run

1. Set up your MySQL database with binary logging enabled
2. Configure environment variables for MySQL connection
3. Install dependencies: `pip install -r requirements.txt`
4. Run: `python main.py`

## Environment variables

### Required MySQL Connection
- **output**: Name of the output topic to write into.
- **MYSQL_HOST**: The IP address or fully qualified domain name of your MySQL server.
- **MYSQL_PORT**: The Port number to use for communication with the server (default: 3306).
- **MYSQL_DATABASE**: The name of the database for CDC.
- **MYSQL_USER**: The username that should be used to interact with the database.
- **MYSQL_PASSWORD**: The password for the user configured above.
- **MYSQL_TABLE**: The name of the table for CDC.

### Optional Configuration
- **MYSQL_SNAPSHOT_HOST**: MySQL host for initial snapshot (defaults to MYSQL_HOST if not set). Use this if you want to perform initial snapshot from a different MySQL instance (e.g., read replica).
- **MYSQL_INITIAL_SNAPSHOT**: Set to "true" to perform initial snapshot of existing data (default: false).
- **MYSQL_SNAPSHOT_BATCH_SIZE**: Number of rows to process in each snapshot batch (default: 1000).
- **MYSQL_FORCE_SNAPSHOT**: Set to "true" to force snapshot even if already completed (default: false).

## Quix Streams StatefulSource

The connector uses Quix Streams' `StatefulSource` class which provides:

- **Automatic State Persistence**: Binlog positions and snapshot status are automatically saved to the state store
- **Exactly-Once Guarantees**: Built-in mechanisms ensure no data loss or duplication
- **Fault Tolerance**: Automatic recovery from failures with consistent state
- **Production-Ready**: Built on Quix Streams' proven architecture

### State Management:
- **Binlog Position**: Automatically tracked as `binlog_position_{schema}_{table}`
- **Snapshot Completion**: Tracked as `snapshot_completed_{schema}_{table}`
- **Transactional Processing**: State changes are committed atomically with message production

Example state data:
```json
{
  "log_file": "mysql-bin.000123",
  "log_pos": 45678,
  "timestamp": 1704067200.0
}
```

## Initial Snapshot

Enable initial snapshot to capture existing table data before starting CDC:

```env
MYSQL_INITIAL_SNAPSHOT=true
MYSQL_SNAPSHOT_BATCH_SIZE=1000
MYSQL_SNAPSHOT_HOST=replica.mysql.example.com  # Optional: use read replica
```

The initial snapshot:
- Processes data in configurable batches to avoid memory issues
- Sends snapshot records with `"kind": "snapshot_insert"` to distinguish from real inserts
- Marks completion in the StatefulSource state store to avoid re-processing on restart
- Can be forced to re-run with `FORCE_SNAPSHOT=true`

## Requirements / Prerequisites

- A MySQL Database with binary logging enabled.
- Set `log-bin=mysql-bin` and `binlog-format=ROW` in MySQL configuration.
- MySQL user with `REPLICATION SLAVE` and `REPLICATION CLIENT` privileges.
- For initial snapshot: `SELECT` privilege on the target table.

### MySQL Configuration Example
```ini
[mysqld]
server-id = 1
log_bin = /var/log/mysql/mysql-bin.log
binlog_expire_logs_seconds = 864000
max_binlog_size = 100M
binlog-format = ROW
binlog_row_metadata = FULL
binlog_row_image = FULL
```

### MySQL User Permissions
```sql
-- Create replication user
CREATE USER 'cdc_user'@'%' IDENTIFIED BY 'secure_password';

-- Grant replication privileges
GRANT REPLICATION SLAVE, REPLICATION CLIENT ON *.* TO 'cdc_user'@'%';

-- Grant select for initial snapshot
GRANT SELECT ON your_database.your_table TO 'cdc_user'@'%';

FLUSH PRIVILEGES;
```

## Change Event Format

### INSERT/Snapshot Insert
```json
{
  "kind": "insert",  // or "snapshot_insert" for initial snapshot
  "schema": "database_name",
  "table": "table_name",
  "columnnames": ["id", "name"],
  "columnvalues": [123, "John Doe"],
  "oldkeys": {}
}
```

### UPDATE
```json
{
  "kind": "update",
  "schema": "database_name",
  "table": "table_name", 
  "columnnames": ["id", "name"],
  "columnvalues": [123, "Jane Doe"],
  "oldkeys": {
    "keynames": ["id", "name"],
    "keyvalues": [123, "John Doe"]
  }
}
```

### DELETE
```json
{
  "kind": "delete",
  "schema": "database_name",
  "table": "table_name",
  "columnnames": [],
  "columnvalues": [],
  "oldkeys": {
    "keynames": ["id", "name"], 
    "keyvalues": [123, "Jane Doe"]
  }
}
```

## Contribute

Submit forked projects to the Quix [GitHub](https://github.com/quixio/quix-samples) repo. Any new project that we accept will be attributed to you and you'll receive $200 in Quix credit.

## Open source

This project is open source under the Apache 2.0 license and available in our [GitHub](https://github.com/quixio/quix-samples) repo.

Please star us and mention us on social to show your appreciation.